from django.db import migrations


def install(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute("""CREATE FUNCTION sams_audit_immutable() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'Audit entries are append-only'; END;
        $$ LANGUAGE plpgsql""")
        schema_editor.execute('CREATE TRIGGER sams_audit_no_mutation BEFORE UPDATE OR DELETE ON audit_auditlog FOR EACH ROW EXECUTE FUNCTION sams_audit_immutable()')
    elif schema_editor.connection.vendor == 'sqlite':
        for action in ('UPDATE', 'DELETE'):
            schema_editor.execute(f"CREATE TRIGGER sams_audit_no_{action.lower()} BEFORE {action} ON audit_auditlog BEGIN SELECT RAISE(ABORT, 'Audit entries are append-only'); END")


def uninstall(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('DROP TRIGGER sams_audit_no_mutation ON audit_auditlog')
        schema_editor.execute('DROP FUNCTION sams_audit_immutable()')
    elif schema_editor.connection.vendor == 'sqlite':
        for action in ('update','delete'):
            schema_editor.execute(f'DROP TRIGGER sams_audit_no_{action}')


class Migration(migrations.Migration):
    dependencies = [('audit', '0001_initial')]
    operations = [migrations.RunPython(install, uninstall)]
