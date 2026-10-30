// Runs only in the isolated GitHub Actions test environment.
import {chromium, firefox, webkit} from 'playwright';
import puppeteer from 'puppeteer-core';
import {snapshot, generateReport} from 'lighthouse';
import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const axeSource = await fs.readFile(require.resolve('axe-core/axe.min.js'), 'utf8');
const url = 'http://localhost:8000';
const dest = new URL('./results/', import.meta.url);
await fs.mkdir(dest, {recursive:true});
const write = (name, value) => fs.writeFile(new URL(name,dest), typeof value === 'string' ? value : JSON.stringify(value,null,2));
const cases=[];
const screens=[
  {name:'login', user:null, role:'ANONYMOUS', view:null},
  {name:'student-attendance', user:'STU001', role:'STUDENT', view:'overview'},
  {name:'faculty-roster', user:'FAC001', role:'FACULTY', view:'attendance'},
  {name:'admin-reports', user:'ADM001', role:'ADMIN', view:'reports'},
  {name:'admin-setup', user:'ADM001', role:'ADMIN', view:'setup'},
  {name:'admin-people', user:'ADM001', role:'ADMIN', view:'users'},
];
function observeApiFailures(page, expectedFailures=[]){
  // Page-local listeners cover the positive audit flow, not other security tests.
  // A deliberate negative request may exempt only its exact method/path/status.
  const failures=[];
  const scopedPath=requestUrl=>{
    const parsed=new URL(requestUrl);
    return parsed.origin===url && parsed.pathname.startsWith('/api/') ? parsed.pathname : null;
  };
  page.on('response',response=>{
    const path=scopedPath(response.url()), status=response.status(), method=response.request().method();
    if(path && status>=400 && !expectedFailures.some(expected=>expected.path===path && expected.method===method && expected.status===status)){
      failures.push(`${method} ${path}: HTTP ${status}`);
    }
  });
  page.on('requestfailed',request=>{
    const path=scopedPath(request.url());
    if(path) failures.push(`${request.method()} ${path}: network failure`);
  });
  return failures;
}
function validateScreenState(screen,state,apiFailures){
  if(apiFailures.length) throw Error('Unexpected API failures: '+apiFailures.join('; '));
  if(state.applicationError) throw Error('Application error: '+state.applicationError);
  if(state.path!==(screen.user ? '/' : '/login/')) throw Error('Wrong page: '+state.path);
  if(state.role!==screen.role) throw Error('Wrong role: '+state.role);
  if(screen.user && state.identity!==screen.user) throw Error('Wrong signed-in identity: '+state.identity);
  const title=screen.user ? ({attendance:'Take attendance',reports:'Reports',setup:'Academic setup',users:'People',overview:'Overview'})[screen.view] : 'Sign in · SAMS';
  if(state.title!==title) throw Error('Wrong view: '+state.title);
  const missing=Object.entries(state.contentChecks).filter(([,present])=>!present).map(([name])=>name);
  if(missing.length) throw Error('Missing expected screen content: '+missing.join(', '));
}
async function assertScreen(page,screen,apiFailures=[]){
  const state=await page.evaluate(screen=>{
    const has=selector=>!!document.querySelector(selector);
    const text=selector=>document.querySelector(selector)?.textContent||'';
    const contains=(selector,value)=>text(selector).includes(value);
    const rows=selector=>document.querySelectorAll(selector+' tbody tr').length>0;
    const contentChecks={};
    if(!screen.user){
      contentChecks.login=has('form[method="post"] #institute_id') && has('form[method="post"] #password') && has('form button[type="submit"]');
    }else if(screen.view==='overview'){
      contentChecks.statistics=document.querySelectorAll('#content .stat strong').length===3;
      contentChecks.sections=rows('#content') && contains('#content','CS341');
      if(screen.role==='ADMIN') contentChecks.settings=has('#threshold-form input[name="threshold"]');
    }else if(screen.view==='attendance'){
      contentChecks.roster=has('#content .mark-form .mark-row select') && contains('#content','STU001') && contains('#content','CS341');
    }else if(screen.view==='reports'){
      contentChecks.filters=has('#report-filter') && has('#csv-link') && has('#pdf-link');
      contentChecks.summary=rows('#report-results') && contains('#report-results','STU001') && contains('#report-results','CS341');
    }else if(screen.view==='setup'){
      contentChecks.forms=['course-form','section-form','slot-form','enroll-form'].every(id=>has('#'+id));
      contentChecks.seededOptions=contains('#section-form select[name="course_id"]','CS341') && contains('#section-form select[name="faculty_id"]','FAC001');
      contentChecks.timetable=rows('#content') && contains('#content table','CS341');
    }else if(screen.view==='users'){
      contentChecks.forms=has('#user-form') && has('#access-form');
      contentChecks.people=rows('#content') && contains('#content table','STU001') && contains('#content table','ADM001');
    }
    return {path:location.pathname,role:document.body.dataset.role||'ANONYMOUS',
      identity:document.querySelector('.sidebar-bottom > span:last-of-type')?.textContent.trim()||null,
      title:screen.user ? text('#page-title').trim() : document.title,width:innerWidth,
      applicationError:text('#notice.error') || text('.auth-form .error') || (contains('#content','Unable to load this view.') ? 'Unable to load this view.' : ''),contentChecks};
  },screen);
  validateScreenState(screen,state,apiFailures);
  return state;
}
async function ready(page){
  if (!page.url().includes('/login/')) {
    await page.locator('#content[aria-busy="false"]').waitFor({timeout:90000});
    // Audit the settled UI, after its entrance animation has finished.
    await page.locator('#content').evaluate(el => Promise.all(
      el.getAnimations({subtree:true}).map(animation => animation.finished.catch(()=>{}))));
  }
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
}
async function signIn(page,user){
  await page.goto(url+'/login/');
  await page.getByLabel('Institute ID',{exact:true}).fill(user);
  await page.getByLabel('Institute ID',{exact:true}).press('Tab');
  if (await page.locator(':focus').getAttribute('name') !== 'password') throw Error('Keyboard order skips password');
  await page.keyboard.type('DemoPass@1234');
  await Promise.all([page.waitForURL(url+'/'), page.keyboard.press('Enter')]);
  await ready(page);
}
async function keyboardView(page,view){
  if(view==='overview') return [];
  const trace=[];
  for(let n=0;n<50;n++){
    await page.keyboard.press('Tab');
    const focus=await page.locator(':focus').evaluate(el=>({tag:el.tagName,name:(el.getAttribute('aria-label')||el.textContent||'').trim().slice(0,90),view:el.getAttribute('data-view'),visible:!!el.getClientRects().length,outline:getComputedStyle(el).outlineStyle}));
    trace.push(focus);
    if(focus.view===view){await page.keyboard.press('Enter');await ready(page);return trace;}
  }
  throw Error('Keyboard navigation could not reach '+view);
}
for(const spec of [
  {name:'google-chrome',engine:chromium,options:{channel:'chrome'}},
  {name:'microsoft-edge',engine:chromium,options:{channel:'msedge'}},
  {name:'firefox',engine:firefox,options:{}},
  {name:'webkit',engine:webkit,options:{}},
]){
  const browser=await spec.engine.launch({headless:true,...spec.options});
  if(spec.name==='google-chrome'){
    // Prove a handled HTTP 500 is rejected by both guards. This control has its
    // own context and evidence file and is excluded from the acceptance count.
    const context=await browser.newContext();
    try{
      const page=await context.newPage();
      const apiFailures=observeApiFailures(page);
      const screen=screens.find(screen=>screen.view==='attendance');
      await signIn(page,screen.user);
      await assertScreen(page,{...screen,view:'overview'},apiFailures);
      await page.route('**/api/sessions/today/',route=>route.fulfill({status:500,contentType:'application/json',body:JSON.stringify({error:{message:'Negative-control API failure'}})}));
      await page.locator('[data-view="attendance"].nav').click();
      await ready(page);
      let apiRejected=false, applicationRejected=false;
      try{await assertScreen(page,screen,apiFailures);}catch(error){apiRejected=error.message.includes('Unexpected API failures: GET /api/sessions/today/: HTTP 500');}
      try{await assertScreen(page,screen);}catch(error){applicationRejected=error.message.includes('Application error:');}
      await write('acceptance-negative-control.json',{result:apiRejected&&applicationRejected?'PASS':'FAIL',apiRejected,applicationRejected,apiFailures,excluded_from_acceptance_count:true});
      if(!apiRejected || !applicationRejected) throw Error('Handled-500 negative control was not rejected');
    }finally{await context.close();}
  }
  for(const width of [1280,360]) for(const screen of screens){
    const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
    const page=await context.newPage();
    page.setDefaultTimeout(90000);
    const errors=[];
    const apiFailures=observeApiFailures(page);
    page.on('pageerror',err=>errors.push(err.message));
    const name=`${spec.name}-${width}-${screen.name}`;
    try{
      if(screen.user){
        await signIn(page,screen.user);
        await assertScreen(page,{...screen,view:'overview'},apiFailures);
      }else await page.goto(url+'/login/');
      const keyboard=screen.view ? await keyboardView(page,screen.view) : [];
      await ready(page);
      await assertScreen(page,screen,apiFailures);
      if(screen.view==='setup'){
        const controls=page.locator('#slot-form select[name="section_id"], #enroll-form select[name="section_id"]');
        if(await controls.count()!==2 || !await controls.evaluateAll(els=>new Set(els.map(e=>e.id)).size===2 && els.every(e=>e.labels.length===1))) throw Error('Section controls need unique IDs and labels');
        await page.locator('#enroll-form textarea').fill('institute_id\nSTU001');
        await page.locator('#enroll-form button').click();
        await page.locator('#notice').filter({hasText:'enrolled.'}).waitFor();
        await ready(page);
      }
      if(screen.view==='users'){
        const controls=page.locator('#user-form select[name="role"], #access-form select[name="role"]');
        if(await controls.count()!==2 || !await controls.evaluateAll(els=>new Set(els.map(e=>e.id)).size===2 && els.every(e=>e.labels.length===1))) throw Error('Role controls need unique IDs and labels');
        await page.locator('#access-form select[name="user_id"]').selectOption({label:'STU001'});
        await page.locator('#access-form select[name="role"]').selectOption('STUDENT');
        await page.locator('#access-form select[name="is_active"]').selectOption('true');
        await page.locator('#access-form button').click();
        await page.locator('#notice').filter({hasText:'Saved successfully.'}).waitFor();
        await ready(page);
      }
      const screenState=await assertScreen(page,screen,apiFailures);
      const title=screenState.title;
      const geometry=await page.evaluate(()=>({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
        horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
        controls:[...document.querySelectorAll('input:not([type=hidden]),select,textarea,button,a')].filter(el=>el.getClientRects().length).length}));
      const scrollChecks=[];
      for(const region of await page.locator('.table-wrap').all()){
        const dimensions=await region.evaluate(el=>({client:el.clientWidth,scroll:el.scrollWidth}));
        if(dimensions.scroll>dimensions.client+1){
          await region.focus();
          await page.keyboard.press('ArrowRight');
          await page.waitForFunction(()=>document.activeElement?.scrollLeft>0);
          scrollChecks.push(await region.evaluate(el=>({focused:document.activeElement===el,scrollLeft:el.scrollLeft,label:el.getAttribute('aria-label')})));
        }
      }
      // Automation injects the audit engine without weakening the application's CSP.
      await page.evaluate(axeSource);
      const axe=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
      await write(name+'-axe.json',axe);
      await write(name+'-keyboard.json',keyboard);
      await write(name+'-semantics.yml',await page.locator('body').ariaSnapshot());
      await page.screenshot({path:new URL(name+'.png',dest).pathname,fullPage:false});
      const failures=axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}));
      await assertScreen(page,screen,apiFailures);
      const result={name,browser:browser.version(),title,screen_state:screenState,geometry,scrollChecks,keyboard_navigation:screen.view==='overview'?'Login keyboard flow only':screen.view?'Tab then Enter to requested view':'Login name/role snapshot',violations:failures,js_errors:errors,
        result:!geometry.horizontalOverflow&&!failures.length&&!errors.length?'PASS':'FAIL'};
      cases.push(result);
    }catch(error){cases.push({name,browser:browser.version(),result:'ERROR',error:error.message,api_failures:apiFailures});}
    await context.close();
    await write('browser-cases.json',{commit_tested:process.env.AUDIT_SOURCE_COMMIT,executed_at_utc:new Date().toISOString(),execution:'Automated isolated CI; no physical-device or human screen-reader claim',cases});
  }
  await browser.close();
}
const docsBrowser=await chromium.launch({headless:true,channel:'chrome'});
try {
  const page=await docsBrowser.newPage();
  const errors=[];
  page.on('pageerror',err=>errors.push(err.message));
  const response=await page.goto(url+'/api/docs/');
  await page.locator('#swagger-ui .opblock').first().waitFor({timeout:60000});
  const schema=await page.request.get(url+'/api/schema/',{headers:{Accept:'application/json'}});
  const parsed=await schema.json();
  const script=await page.request.get(url+'/api/docs/?script=');
  const dashboard=await page.request.get(url+'/login/');
  const policy=dashboard.headers()['content-security-policy']||'';
  if(response.status()!==200 || !parsed.paths?.['/api/health/'] ||
      !script.headers()['content-type']?.startsWith('application/javascript') ||
      !policy.includes("script-src 'self';") || policy.includes('unsafe-inline') ||
      !response.headers()['x-content-type-options'] || errors.length) throw Error('Swagger/schema/CSP regression: '+JSON.stringify(errors));
  cases.push({name:'api-docs-through-nginx',result:'PASS',operations:await page.locator('#swagger-ui .opblock').count()});
  await page.screenshot({path:new URL('api-docs.png',dest).pathname,fullPage:false});
} catch(error) { cases.push({name:'api-docs-through-nginx',result:'ERROR',error:error.message}); }
finally { await docsBrowser.close(); }
await write('browser-cases.json',{commit_tested:process.env.AUDIT_SOURCE_COMMIT,executed_at_utc:new Date().toISOString(),execution:'Automated isolated CI; no physical-device or human screen-reader claim',cases});
const chrome=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
{
  const context=await chrome.createBrowserContext();
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(url+'/api/docs/');
  await page.waitForSelector('.swagger-ui .opblock',{timeout:90000});
  const operations=await page.$$eval('.swagger-ui .opblock',rows=>rows.length);
  await page.screenshot({path:new URL('api-docs-strict-csp.png',dest).pathname});
  await write('api-docs-strict-csp.json',{operations,js_errors:errors,result:operations>0&&!errors.length?'PASS':'FAIL'});
  if(!operations||errors.length) process.exitCode=1;
  await context.close();
}
const lighthouse=[];
for(const screen of screens){
  const context=await chrome.createBrowserContext();
  const page=await context.newPage();
  await page.setViewport({width:360,height:900,deviceScaleFactor:1});
  const apiFailures=observeApiFailures(page);
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(url+'/login/');
  if(screen.user){
    await page.type('#institute_id',screen.user);
    await page.type('#password','DemoPass@1234');
    await Promise.all([page.waitForNavigation(),page.click('button[type="submit"],form button')]);
    await page.waitForSelector('#content[aria-busy="false"]',{timeout:90000});
    await assertScreen(page,{...screen,view:'overview'},apiFailures);
    if(screen.view!=='overview'){
      await page.click(`[data-view="${screen.view}"]`);
      await page.waitForSelector('#content[aria-busy="false"]',{timeout:90000});
    }
  }
  await page.waitForNetworkIdle();
  await page.evaluate(()=>Promise.all([document.fonts.ready,...document.getAnimations().map(animation=>animation.finished.catch(()=>{}))]));
  const actual=await assertScreen(page,screen,apiFailures);
  const result=await snapshot(page,{flags:{onlyCategories:['accessibility'],formFactor:'mobile',screenEmulation:{disabled:true}}});
  await assertScreen(page,screen,apiFailures);
  if(errors.length) throw Error('Lighthouse page errors: '+errors.join('; '));
  await write(screen.name+'-lighthouse.json',result.lhr);
  await write(screen.name+'-lighthouse.html',generateReport(result.lhr));
  const failed=Object.values(result.lhr.audits).filter(a=>a.score===0).map(a=>a.id);
  lighthouse.push({screen:screen.name,actual,score:result.lhr.categories.accessibility.score*100,failed_audits:failed});
  await context.close();
}
await chrome.close();
await write('lighthouse-summary.json',{commit_tested:process.env.AUDIT_SOURCE_COMMIT,snapshots:lighthouse,limitation:'Accessibility snapshots; not navigation performance or manual assistive-technology certification.'});
console.log(JSON.stringify({browser_cases:cases.length,failed:cases.filter(c=>c.result!=='PASS'),lighthouse},null,2));
if(cases.some(c=>c.result!=='PASS')||lighthouse.some(l=>l.score<90||l.failed_audits.includes('color-contrast'))) process.exitCode=1;
