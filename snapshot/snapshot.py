import boto3
import click

session = boto3.Session(profile_name='snapshot');
ec2=session.resource('ec2')

def filter_instances(project):
    instance=[]

    if project:
        filters = [{'Name':'tag:project', 'Values':[project]}]
        instance=ec2.instances.filter(Filters=filters)
    else:
        instance=ec2.instances.all()

    return(instance)

@click.group()
def cli():
    """snapshot manages snapshots and instances"""


@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project',default=None,
    help="Only snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    "List Snapshots"

    instance=filter_instances(project)

    for i in instance:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))
    return


@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project',default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List Volumes"

    instance=filter_instances(project)

    for i in instance:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return



@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot')
@click.option('--project',default=None,
    help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshot for EC2 Instances"
    instance=filter_instances(project)

    for i in instance:
        
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by snapshot cli")

        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()

    print("Job Done")
    return

@instances.command('list')
@click.option('--project',default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List Instances"
    instance=filter_instances(project)

    for i in instance:
        tags = { t['Key']:t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.state['Name'],
            i.public_dns_name,
            tags.get('project','<no project>')
        )))
    return

@instances.command('stop')
@click.option('--project',default=None,
    help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Stop EC2 Instances"
    instance=filter_instances(project)
    for i in instance:
        print("Stopping {0}.....".format(i.id))
        i.stop()
    return

@instances.command('start')
@click.option('--project',default=None,
    help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Start EC2 Instances"
    instance=filter_instances(project)
    for i in instance:
        print("Starting {0}.....".format(i.id))
        i.start()
    return

if __name__ == '__main__':
    cli()
