import sys
import requests


class SchedulerConnector:
    # TODO make algorithm configurable via cli
    def __init__(self, url, algorithm):
        self.url = url
        self.algorithm = algorithm
        self.id = None

    def register_wf(self, wf_name, task_data, cluster_data):
        if self.id is not None:
            # TODO handle error
            assert False
        data = {
            'algorithm': self.algorithm,
            'workflow': {
                'name': wf_name,
                'tasks': task_data,
            },
            'cluster': {
                'machines': cluster_data,
            },
        }
        print(data['algorithm'])
        try:
            r = requests.post(f'{self.url}/wf/new', json=data, timeout=1)
        except requests.ConnectionError:
            print('error connecting to scheduler', file=sys.stderr)
            exit(-1)
        if not r.status_code == 200:
            print('Unable to register workflow. Server returned:', file=sys.stderr)
            print(r.status_code, r.text, file=sys.stderr)
            exit(-1)
        j = r.json()
        self.id = j['id']
        return j['schedule']

    def update_wf(self, finished_tasks, running_tasks):
        data = {
            'finished_tasks': finished_tasks,
            'running_tasks': running_tasks,
        }
        try:
            r = requests.post(
                f'{self.url}/wf/{self.id}/update', json=data, timeout=1)
        except requests.ConnectionError:
            print('error connecting to scheduler', file=sys.stderr)
            exit(-1)
        if not r.status_code == 200:
            print('Unable to update workflow. Server returned:', file=sys.stderr)
            print(r.status_code, r.text, file=sys.stderr)
            exit(-1)
        j = r.json()
        return j['schedule']
