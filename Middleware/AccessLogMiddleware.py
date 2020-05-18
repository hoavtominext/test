import logging
import socket
import os

from django.utils.deprecation import MiddlewareMixin

hosts = socket.gethostbyname_ex(socket.gethostname())
server = hosts[len(hosts) - 1][0]


class Middleware(MiddlewareMixin):

    def __call__(self, request):
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_response(self, request, response):
        path_access_log = os.getenv('PATH_ACCESS_LOG', 'access_logger.log')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        client_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        method = request.method,
        path = request.META['PATH_INFO']
        user_id = 'anonymous'
        status_code = response.status_code
        if hasattr(request, 'user') and request.user is not None:
            user_id = request.user.id if request.user.id else 'anonymous'

        logging.basicConfig(filename=path_access_log,
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
        message = "API access log at {}".format({
            'client_ip': client_ip,
            'user_id': user_id,
            'method': method,
            'path': path,
            'status_code': status_code
        })
        logging.info(message)
        return response
