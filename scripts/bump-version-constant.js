module.exports.readVersion = function (contents) {
  return (contents.match(/CLI_VERSION = '(\d+\.\d+\.\d+)'/) || [])[1];
}

module.exports.writeVersion = function (contents, version) {
  return contents.replace(/(CLI_VERSION = ')(\d+\.\d+\.\d+)/g, `$1${version}`)
}
