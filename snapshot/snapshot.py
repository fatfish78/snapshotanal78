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
def instances():
    """Commands for instances"""


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
    instances()
