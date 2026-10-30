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
  {name:'login', user:null, view:null},
  {name:'student-attendance', user:'STU001', view:'overview'},
  {name:'faculty-roster', user:'FAC001', view:'attendance'},
  {name:'admin-reports', user:'ADM001', view:'reports'},
];
async function ready(page){
  if (!page.url().includes('/login/')) await page.locator('#content[aria-busy="false"]').waitFor({timeout:90000});
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
  for(const width of [1280,360]) for(const screen of screens){
    const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
    const page=await context.newPage();
    page.setDefaultTimeout(90000);
    const errors=[];
    page.on('pageerror',err=>errors.push(err.message));
    const name=`${spec.name}-${width}-${screen.name}`;
    try{
      if(screen.user) await signIn(page,screen.user); else await page.goto(url+'/login/');
      const keyboard=screen.view ? await keyboardView(page,screen.view) : [];
      await ready(page);
      const title=screen.user ? await page.locator('#page-title').textContent() : await page.title();
      if(screen.view==='attendance' && title!=='Take attendance') throw Error('Wrong roster view');
      if(screen.view==='reports' && title!=='Reports') throw Error('Wrong report view');
      const geometry=await page.evaluate(()=>({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,
        horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,
        controls:[...document.querySelectorAll('input:not([type=hidden]),select,textarea,button,a')].filter(el=>el.getClientRects().length).length}));
      // Automation injects the audit engine without weakening the application's CSP.
      await page.evaluate(axeSource);
      const axe=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
      await write(name+'-axe.json',axe);
      await write(name+'-keyboard.json',keyboard);
      await write(name+'-semantics.yml',await page.locator('body').ariaSnapshot());
      await page.screenshot({path:new URL(name+'.png',dest).pathname,fullPage:false});
      const failures=axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}));
      const result={name,browser:browser.version(),title,geometry,keyboard_navigation:screen.view==='overview'?'Login keyboard flow only':screen.view?'Tab then Enter to requested view':'Login name/role snapshot',violations:failures,js_errors:errors,
        result:!geometry.horizontalOverflow&&!failures.length&&!errors.length?'PASS':'FAIL'};
      cases.push(result);
    }catch(error){cases.push({name,browser:browser.version(),result:'ERROR',error:error.message});}
    await context.close();
    await write('browser-cases.json',{commit_tested:process.env.AUDIT_SOURCE_COMMIT,executed_at_utc:new Date().toISOString(),execution:'Automated isolated CI; no physical-device or human screen-reader claim',cases});
  }
  await browser.close();
}
const chrome=await puppeteer.launch({executablePath:'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
const lighthouse=[];
for(const screen of screens){
  const context=await chrome.createBrowserContext();
  const page=await context.newPage();
  await page.setViewport({width:360,height:900,deviceScaleFactor:1});
  await page.goto(url+'/login/');
  if(screen.user){
    await page.type('#institute_id',screen.user);
    await page.type('#password','DemoPass@1234');
    await Promise.all([page.waitForNavigation(),page.click('button[type="submit"],form button')]);
    await page.waitForSelector('#content[aria-busy="false"]',{timeout:90000});
    if(screen.view!=='overview'){
      await page.click(`[data-view="${screen.view}"]`);
      await page.waitForSelector('#content[aria-busy="false"]',{timeout:90000});
    }
  }
  const actual=await page.evaluate(()=>({title:document.querySelector('#page-title')?.textContent||document.title,role:document.body.dataset.role||'ANONYMOUS',width:innerWidth}));
  const result=await snapshot(page,{flags:{onlyCategories:['accessibility'],formFactor:'mobile',screenEmulation:{disabled:true}}});
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
