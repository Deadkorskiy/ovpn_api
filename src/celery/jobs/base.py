class BaseJob(object):

    def do_work(self, *args, **kwargs):
        raise NotImplementedError
