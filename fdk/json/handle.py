# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import types
import ujson

from fdk import errors
from fdk import headers
from fdk.json import response


def normal_dispatch(app, context, data=None, loop=None):
    """
    Request handler app dispatcher
    :param app: request handler app
    :type app: types.Callable
    :param context: request context
    :type context: request.RequestContext
    :param data: request body
    :type data: io.BufferedIOBase
    :param loop: asyncio event loop
    :type loop: asyncio.AbstractEventLoop
    :return: raw response
    :rtype: response.RawResponse
    """
    try:
        rs = app(context, data=data, loop=loop)
        if isinstance(rs, response.RawResponse):
            return rs
        elif isinstance(rs, types.CoroutineType):
            return loop.run_until_complete(rs)
        elif isinstance(rs, str):
            hs = headers.GoLikeHeaders({})
            hs.set('content-type', 'text/plain')
            return response.RawResponse(response_data=rs)
        elif isinstance(rs, bytes):
            hs = headers.GoLikeHeaders({})
            hs.set('content-type', 'application/octet-stream')
            return response.RawResponse(
                response_data=rs.decode("utf8"),
                headers=hs,
                status_code=200
            )
        else:
            hs = headers.GoLikeHeaders({})
            hs.set('content-type', 'application/json')
            return response.RawResponse(
                ujson.dumps(rs),
                headers=hs,
                status_code=200,
            )
    except errors.JSONDispatchException as e:
        return e.response()
    except Exception as ex:
        return errors.JSONDispatchException(500, str(ex)).response()
