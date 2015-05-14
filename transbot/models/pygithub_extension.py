try:
    import github
    import github.GithubObject.NotSet as NotSet
except ImportError:
    github = None
    NotSet = None
from hashlib import sha1
import base64


def __get_file_sha1(file_content):
    return sha1("blob %s\0%s" % (len(file_content), file_content)).hexdigest()


def put_file_contents(self, path, message, content, sha=None,
                      ref=NotSet):
    """
    :calls: `PUT /repos/:owner/:repo/contents/:path
      <http://developer.github.com/v3/repos/contents>`_
    :param path: string
    :param message: string
    :param content: string
    :param ref: string
    :rtype: None
    """
    assert isinstance(path, (str, unicode)), path
    assert isinstance(path, (str, unicode)), message
    assert isinstance(path, (str, unicode)), content
    assert ref is NotSet or isinstance(ref, (str, unicode)), ref
    content = content.encode('utf-8')
    data = dict()
    data["message"] = message
    data["content"] = base64.b64encode(content)
    data["sha"] = sha or __get_file_sha1(data["content"])
    if ref is not NotSet:
        data["branch"] = ref
    self._requester.requestJsonAndCheck(
        "PUT", self.url + "/contents" + path, input=data)


def delete_file(self, path, message, sha, ref=NotSet):
    """
    :calls: `DELETE /repos/:owner/:repo/contents/:path
      <http://developer.github.com/v3/repos/contents>`_
    :param path: string
    :param message: string
    :param ref: string
    :rtype: None
    """
    assert isinstance(path, (str, unicode)), path
    assert isinstance(path, (str, unicode)), message
    assert ref is NotSet or isinstance(ref, (str, unicode)), ref
    data = dict()
    data["message"] = message
    data["sha"] = sha
    if ref is not NotSet:
        data["branch"] = ref
    self._requester.requestJsonAndCheck(
        "DELETE", self.url + "/contents" + path, input=data)


# Monkey-patching lib, because these methods are not present
if github:
    github.Repository.Repository.put_file_contents = put_file_contents
    github.Repository.Repository.delete_file = delete_file
