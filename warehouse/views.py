# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyramid.httpexceptions import (
    HTTPException, HTTPSeeOther, HTTPMovedPermanently,
)
from pyramid.view import (
    notfound_view_config, forbidden_view_config, view_config,
)

from warehouse.accounts import REDIRECT_FIELD_NAME
from warehouse.csrf import csrf_exempt
from warehouse.packaging.models import Project, Release, File
from warehouse.accounts.models import User


@view_config(context=HTTPException, decorator=[csrf_exempt])
@notfound_view_config(
    append_slash=HTTPMovedPermanently,
    decorator=[csrf_exempt],
)
def exception_view(exc, request):
    return exc


@forbidden_view_config()
def forbidden(exc, request):
    # If the forbidden error is because the user isn't logged in, then we'll
    # redirect them to the log in page.
    if request.authenticated_userid is None:
        url = request.route_url(
            "accounts.login",
            _query={REDIRECT_FIELD_NAME: request.path_qs},
        )
        return HTTPSeeOther(url)

    # If we've reached here, then the user is logged in and they are genuinely
    # not allowed to access this page.
    # TODO: Style the forbidden page.
    return exc


@view_config(
    route_name="index",
    renderer="index.html",
)
def index(request):
    latest_updated_releases = request.db.query(Release)\
                                        .order_by(Release.created.desc())[:20]
    num_projects = request.db.query(Project).count()
    num_users = request.db.query(User).count()
    num_files = request.db.query(File).count()
    num_releases = request.db.query(Release).count()

    return {
        'latest_updated_releases': latest_updated_releases,
        'num_projects': num_projects,
        'num_users': num_users,
        'num_releases': num_releases,
        'num_files': num_files,
    }
