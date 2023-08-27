"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.addPathToAdapterConfig = addPathToAdapterConfig;
exports.generateInstallAdapterCommand = generateInstallAdapterCommand;
exports.getGitRootPath = getGitRootPath;
exports.getInstallStringMappings = getInstallStringMappings;
exports.getNearestNodeModulesDirectory = getNearestNodeModulesDirectory;
exports.getNearestProjectRootDirectory = getNearestProjectRootDirectory;
exports.getPrompter = getPrompter;
exports.resolveAdapterPath = resolveAdapterPath;
var _child_process = _interopRequireDefault(require("child_process"));
var _path = _interopRequireDefault(require("path"));
var _fs = _interopRequireDefault(require("fs"));
var _findNodeModules = _interopRequireDefault(require("find-node-modules"));
var _lodash = _interopRequireDefault(require("lodash"));
var _detectIndent = _interopRequireDefault(require("detect-indent"));
var _util = require("../common/util");
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
function cov_16lcdpz3tp() {
  var path = "/home/runner/work/cz-cli/cz-cli/src/commitizen/adapter.js";
  var hash = "e37ec3ccafde4f581a254419294338bc76165289";
  var global = new Function("return this")();
  var gcv = "__coverage__";
  var coverageData = {
    path: "/home/runner/work/cz-cli/cz-cli/src/commitizen/adapter.js",
    statementMap: {
      "0": {
        start: {
          line: 36,
          column: 32
        },
        end: {
          line: 42,
          column: 3
        }
      },
      "1": {
        start: {
          line: 44,
          column: 24
        },
        end: {
          line: 44,
          column: 91
        }
      },
      "2": {
        start: {
          line: 45,
          column: 26
        },
        end: {
          line: 45,
          column: 67
        }
      },
      "3": {
        start: {
          line: 47,
          column: 15
        },
        end: {
          line: 47,
          column: 61
        }
      },
      "4": {
        start: {
          line: 48,
          column: 27
        },
        end: {
          line: 48,
          column: 56
        }
      },
      "5": {
        start: {
          line: 49,
          column: 30
        },
        end: {
          line: 49,
          column: 32
        }
      },
      "6": {
        start: {
          line: 50,
          column: 2
        },
        end: {
          line: 52,
          column: 3
        }
      },
      "7": {
        start: {
          line: 51,
          column: 4
        },
        end: {
          line: 51,
          column: 81
        }
      },
      "8": {
        start: {
          line: 53,
          column: 2
        },
        end: {
          line: 53,
          column: 96
        }
      },
      "9": {
        start: {
          line: 60,
          column: 2
        },
        end: {
          line: 60,
          column: 70
        }
      },
      "10": {
        start: {
          line: 67,
          column: 26
        },
        end: {
          line: 67,
          column: 35
        }
      },
      "11": {
        start: {
          line: 68,
          column: 34
        },
        end: {
          line: 72,
          column: 3
        }
      },
      "12": {
        start: {
          line: 74,
          column: 2
        },
        end: {
          line: 74,
          column: 68
        }
      },
      "13": {
        start: {
          line: 81,
          column: 2
        },
        end: {
          line: 81,
          column: 121
        }
      },
      "14": {
        start: {
          line: 90,
          column: 31
        },
        end: {
          line: 90,
          column: 55
        }
      },
      "15": {
        start: {
          line: 95,
          column: 2
        },
        end: {
          line: 99,
          column: 3
        }
      },
      "16": {
        start: {
          line: 96,
          column: 4
        },
        end: {
          line: 96,
          column: 37
        }
      },
      "17": {
        start: {
          line: 106,
          column: 2
        },
        end: {
          line: 106,
          column: 78
        }
      },
      "18": {
        start: {
          line: 113,
          column: 14
        },
        end: {
          line: 117,
          column: 48
        }
      },
      "19": {
        start: {
          line: 119,
          column: 15
        },
        end: {
          line: 122,
          column: 48
        }
      },
      "20": {
        start: {
          line: 124,
          column: 15
        },
        end: {
          line: 127,
          column: 57
        }
      },
      "21": {
        start: {
          line: 129,
          column: 14
        },
        end: {
          line: 129,
          column: 33
        }
      },
      "22": {
        start: {
          line: 131,
          column: 2
        },
        end: {
          line: 131,
          column: 36
        }
      },
      "23": {
        start: {
          line: 139,
          column: 28
        },
        end: {
          line: 139,
          column: 59
        }
      },
      "24": {
        start: {
          line: 142,
          column: 16
        },
        end: {
          line: 142,
          column: 44
        }
      },
      "25": {
        start: {
          line: 160,
          column: 15
        },
        end: {
          line: 160,
          column: 45
        }
      },
      "26": {
        start: {
          line: 161,
          column: 15
        },
        end: {
          line: 161,
          column: 68
        }
      },
      "27": {
        start: {
          line: 164,
          column: 28
        },
        end: {
          line: 166,
          column: 22
        }
      },
      "28": {
        start: {
          line: 168,
          column: 2
        },
        end: {
          line: 174,
          column: 3
        }
      },
      "29": {
        start: {
          line: 170,
          column: 4
        },
        end: {
          line: 170,
          column: 48
        }
      },
      "30": {
        start: {
          line: 172,
          column: 4
        },
        end: {
          line: 172,
          column: 86
        }
      },
      "31": {
        start: {
          line: 173,
          column: 4
        },
        end: {
          line: 173,
          column: 16
        }
      },
      "32": {
        start: {
          line: 178,
          column: 2
        },
        end: {
          line: 178,
          column: 109
        }
      }
    },
    fnMap: {
      "0": {
        name: "addPathToAdapterConfig",
        decl: {
          start: {
            line: 34,
            column: 9
          },
          end: {
            line: 34,
            column: 31
          }
        },
        loc: {
          start: {
            line: 34,
            column: 68
          },
          end: {
            line: 54,
            column: 1
          }
        },
        line: 34
      },
      "1": {
        name: "getInstallOptions",
        decl: {
          start: {
            line: 59,
            column: 9
          },
          end: {
            line: 59,
            column: 26
          }
        },
        loc: {
          start: {
            line: 59,
            column: 43
          },
          end: {
            line: 61,
            column: 1
          }
        },
        line: 59
      },
      "2": {
        name: "getInstallCommand",
        decl: {
          start: {
            line: 66,
            column: 9
          },
          end: {
            line: 66,
            column: 26
          }
        },
        loc: {
          start: {
            line: 66,
            column: 43
          },
          end: {
            line: 75,
            column: 1
          }
        },
        line: 66
      },
      "3": {
        name: "generateInstallAdapterCommand",
        decl: {
          start: {
            line: 80,
            column: 9
          },
          end: {
            line: 80,
            column: 38
          }
        },
        loc: {
          start: {
            line: 80,
            column: 95
          },
          end: {
            line: 82,
            column: 1
          }
        },
        line: 80
      },
      "4": {
        name: "getNearestNodeModulesDirectory",
        decl: {
          start: {
            line: 87,
            column: 9
          },
          end: {
            line: 87,
            column: 39
          }
        },
        loc: {
          start: {
            line: 87,
            column: 50
          },
          end: {
            line: 100,
            column: 1
          }
        },
        line: 87
      },
      "5": {
        name: "getNearestProjectRootDirectory",
        decl: {
          start: {
            line: 105,
            column: 9
          },
          end: {
            line: 105,
            column: 39
          }
        },
        loc: {
          start: {
            line: 105,
            column: 60
          },
          end: {
            line: 107,
            column: 1
          }
        },
        line: 105
      },
      "6": {
        name: "getInstallStringMappings",
        decl: {
          start: {
            line: 112,
            column: 9
          },
          end: {
            line: 112,
            column: 33
          }
        },
        loc: {
          start: {
            line: 112,
            column: 99
          },
          end: {
            line: 132,
            column: 1
          }
        },
        line: 112
      },
      "7": {
        name: "getPrompter",
        decl: {
          start: {
            line: 137,
            column: 9
          },
          end: {
            line: 137,
            column: 20
          }
        },
        loc: {
          start: {
            line: 137,
            column: 35
          },
          end: {
            line: 152,
            column: 1
          }
        },
        line: 137
      },
      "8": {
        name: "resolveAdapterPath",
        decl: {
          start: {
            line: 158,
            column: 9
          },
          end: {
            line: 158,
            column: 27
          }
        },
        loc: {
          start: {
            line: 158,
            column: 49
          },
          end: {
            line: 175,
            column: 1
          }
        },
        line: 158
      },
      "9": {
        name: "getGitRootPath",
        decl: {
          start: {
            line: 177,
            column: 9
          },
          end: {
            line: 177,
            column: 23
          }
        },
        loc: {
          start: {
            line: 177,
            column: 27
          },
          end: {
            line: 179,
            column: 1
          }
        },
        line: 177
      }
    },
    branchMap: {
      "0": {
        loc: {
          start: {
            line: 47,
            column: 15
          },
          end: {
            line: 47,
            column: 61
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 47,
            column: 15
          },
          end: {
            line: 47,
            column: 53
          }
        }, {
          start: {
            line: 47,
            column: 57
          },
          end: {
            line: 47,
            column: 61
          }
        }],
        line: 47
      },
      "1": {
        loc: {
          start: {
            line: 50,
            column: 2
          },
          end: {
            line: 52,
            column: 3
          }
        },
        type: "if",
        locations: [{
          start: {
            line: 50,
            column: 2
          },
          end: {
            line: 52,
            column: 3
          }
        }, {
          start: {
            line: undefined,
            column: undefined
          },
          end: {
            line: undefined,
            column: undefined
          }
        }],
        line: 50
      },
      "2": {
        loc: {
          start: {
            line: 74,
            column: 9
          },
          end: {
            line: 74,
            column: 67
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 74,
            column: 9
          },
          end: {
            line: 74,
            column: 48
          }
        }, {
          start: {
            line: 74,
            column: 52
          },
          end: {
            line: 74,
            column: 67
          }
        }],
        line: 74
      },
      "3": {
        loc: {
          start: {
            line: 80,
            column: 71
          },
          end: {
            line: 80,
            column: 93
          }
        },
        type: "default-arg",
        locations: [{
          start: {
            line: 80,
            column: 88
          },
          end: {
            line: 80,
            column: 93
          }
        }],
        line: 80
      },
      "4": {
        loc: {
          start: {
            line: 95,
            column: 2
          },
          end: {
            line: 99,
            column: 3
          }
        },
        type: "if",
        locations: [{
          start: {
            line: 95,
            column: 2
          },
          end: {
            line: 99,
            column: 3
          }
        }],
        line: 95
      },
      "5": {
        loc: {
          start: {
            line: 95,
            column: 6
          },
          end: {
            line: 95,
            column: 65
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 95,
            column: 6
          },
          end: {
            line: 95,
            column: 28
          }
        }, {
          start: {
            line: 95,
            column: 32
          },
          end: {
            line: 95,
            column: 65
          }
        }],
        line: 95
      },
      "6": {
        loc: {
          start: {
            line: 114,
            column: 17
          },
          end: {
            line: 114,
            column: 56
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 114,
            column: 36
          },
          end: {
            line: 114,
            column: 44
          }
        }, {
          start: {
            line: 114,
            column: 47
          },
          end: {
            line: 114,
            column: 56
          }
        }],
        line: 114
      },
      "7": {
        loc: {
          start: {
            line: 114,
            column: 17
          },
          end: {
            line: 114,
            column: 33
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 114,
            column: 17
          },
          end: {
            line: 114,
            column: 21
          }
        }, {
          start: {
            line: 114,
            column: 25
          },
          end: {
            line: 114,
            column: 33
          }
        }],
        line: 114
      },
      "8": {
        loc: {
          start: {
            line: 115,
            column: 20
          },
          end: {
            line: 115,
            column: 54
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 115,
            column: 30
          },
          end: {
            line: 115,
            column: 42
          }
        }, {
          start: {
            line: 115,
            column: 45
          },
          end: {
            line: 115,
            column: 54
          }
        }],
        line: 115
      },
      "9": {
        loc: {
          start: {
            line: 116,
            column: 22
          },
          end: {
            line: 116,
            column: 60
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 116,
            column: 34
          },
          end: {
            line: 116,
            column: 48
          }
        }, {
          start: {
            line: 116,
            column: 51
          },
          end: {
            line: 116,
            column: 60
          }
        }],
        line: 116
      },
      "10": {
        loc: {
          start: {
            line: 117,
            column: 18
          },
          end: {
            line: 117,
            column: 47
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 117,
            column: 26
          },
          end: {
            line: 117,
            column: 35
          }
        }, {
          start: {
            line: 117,
            column: 38
          },
          end: {
            line: 117,
            column: 47
          }
        }],
        line: 117
      },
      "11": {
        loc: {
          start: {
            line: 120,
            column: 16
          },
          end: {
            line: 120,
            column: 41
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 120,
            column: 22
          },
          end: {
            line: 120,
            column: 29
          }
        }, {
          start: {
            line: 120,
            column: 32
          },
          end: {
            line: 120,
            column: 41
          }
        }],
        line: 120
      },
      "12": {
        loc: {
          start: {
            line: 121,
            column: 18
          },
          end: {
            line: 121,
            column: 47
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 121,
            column: 26
          },
          end: {
            line: 121,
            column: 35
          }
        }, {
          start: {
            line: 121,
            column: 38
          },
          end: {
            line: 121,
            column: 47
          }
        }],
        line: 121
      },
      "13": {
        loc: {
          start: {
            line: 122,
            column: 18
          },
          end: {
            line: 122,
            column: 47
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 122,
            column: 26
          },
          end: {
            line: 122,
            column: 35
          }
        }, {
          start: {
            line: 122,
            column: 38
          },
          end: {
            line: 122,
            column: 47
          }
        }],
        line: 122
      },
      "14": {
        loc: {
          start: {
            line: 125,
            column: 17
          },
          end: {
            line: 125,
            column: 61
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 125,
            column: 36
          },
          end: {
            line: 125,
            column: 49
          }
        }, {
          start: {
            line: 125,
            column: 52
          },
          end: {
            line: 125,
            column: 61
          }
        }],
        line: 125
      },
      "15": {
        loc: {
          start: {
            line: 125,
            column: 17
          },
          end: {
            line: 125,
            column: 33
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 125,
            column: 17
          },
          end: {
            line: 125,
            column: 21
          }
        }, {
          start: {
            line: 125,
            column: 25
          },
          end: {
            line: 125,
            column: 33
          }
        }],
        line: 125
      },
      "16": {
        loc: {
          start: {
            line: 126,
            column: 16
          },
          end: {
            line: 126,
            column: 50
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 126,
            column: 26
          },
          end: {
            line: 126,
            column: 38
          }
        }, {
          start: {
            line: 126,
            column: 41
          },
          end: {
            line: 126,
            column: 50
          }
        }],
        line: 126
      },
      "17": {
        loc: {
          start: {
            line: 127,
            column: 18
          },
          end: {
            line: 127,
            column: 56
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 127,
            column: 30
          },
          end: {
            line: 127,
            column: 44
          }
        }, {
          start: {
            line: 127,
            column: 47
          },
          end: {
            line: 127,
            column: 56
          }
        }],
        line: 127
      },
      "18": {
        loc: {
          start: {
            line: 131,
            column: 9
          },
          end: {
            line: 131,
            column: 35
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 131,
            column: 9
          },
          end: {
            line: 131,
            column: 28
          }
        }, {
          start: {
            line: 131,
            column: 32
          },
          end: {
            line: 131,
            column: 35
          }
        }],
        line: 131
      },
      "19": {
        loc: {
          start: {
            line: 161,
            column: 15
          },
          end: {
            line: 161,
            column: 68
          }
        },
        type: "binary-expr",
        locations: [{
          start: {
            line: 161,
            column: 15
          },
          end: {
            line: 161,
            column: 36
          }
        }, {
          start: {
            line: 161,
            column: 40
          },
          end: {
            line: 161,
            column: 68
          }
        }],
        line: 161
      },
      "20": {
        loc: {
          start: {
            line: 164,
            column: 28
          },
          end: {
            line: 166,
            column: 22
          }
        },
        type: "cond-expr",
        locations: [{
          start: {
            line: 165,
            column: 4
          },
          end: {
            line: 165,
            column: 54
          }
        }, {
          start: {
            line: 166,
            column: 4
          },
          end: {
            line: 166,
            column: 22
          }
        }],
        line: 164
      }
    },
    s: {
      "0": 0,
      "1": 0,
      "2": 0,
      "3": 0,
      "4": 0,
      "5": 0,
      "6": 0,
      "7": 0,
      "8": 0,
      "9": 0,
      "10": 0,
      "11": 0,
      "12": 0,
      "13": 0,
      "14": 0,
      "15": 0,
      "16": 0,
      "17": 0,
      "18": 0,
      "19": 0,
      "20": 0,
      "21": 0,
      "22": 0,
      "23": 0,
      "24": 0,
      "25": 0,
      "26": 0,
      "27": 0,
      "28": 0,
      "29": 0,
      "30": 0,
      "31": 0,
      "32": 0
    },
    f: {
      "0": 0,
      "1": 0,
      "2": 0,
      "3": 0,
      "4": 0,
      "5": 0,
      "6": 0,
      "7": 0,
      "8": 0,
      "9": 0
    },
    b: {
      "0": [0, 0],
      "1": [0, 0],
      "2": [0, 0],
      "3": [0],
      "4": [0],
      "5": [0, 0],
      "6": [0, 0],
      "7": [0, 0],
      "8": [0, 0],
      "9": [0, 0],
      "10": [0, 0],
      "11": [0, 0],
      "12": [0, 0],
      "13": [0, 0],
      "14": [0, 0],
      "15": [0, 0],
      "16": [0, 0],
      "17": [0, 0],
      "18": [0, 0],
      "19": [0, 0],
      "20": [0, 0]
    },
    _coverageSchema: "1a1c01bbd47fc00a2c39e90264f33305004495a9",
    hash: "e37ec3ccafde4f581a254419294338bc76165289"
  };
  var coverage = global[gcv] || (global[gcv] = {});
  if (!coverage[path] || coverage[path].hash !== hash) {
    coverage[path] = coverageData;
  }
  var actualCoverage = coverage[path];
  {
    // @ts-ignore
    cov_16lcdpz3tp = function () {
      return actualCoverage;
    };
  }
  return actualCoverage;
}
cov_16lcdpz3tp();
/**
 * ADAPTER
 *
 * Adapter is generally responsible for actually installing adapters to an
 * end user's project. It does not perform checks to determine if there is
 * a previous commitizen adapter installed or if the proper fields were
 * provided. It defers that responsibility to init.
 */

/**
 * Modifies the package.json, sets config.commitizen.path to the path of the adapter
 * Must be passed an absolute path to the cli's root
 */
function addPathToAdapterConfig(cliPath, repoPath, adapterNpmName) {
  cov_16lcdpz3tp().f[0]++;
  let commitizenAdapterConfig = (cov_16lcdpz3tp().s[0]++, {
    config: {
      commitizen: {
        path: `./node_modules/${adapterNpmName}`
      }
    }
  });
  let packageJsonPath = (cov_16lcdpz3tp().s[1]++, _path.default.join(getNearestProjectRootDirectory(repoPath), 'package.json'));
  let packageJsonString = (cov_16lcdpz3tp().s[2]++, _fs.default.readFileSync(packageJsonPath, 'utf-8'));
  // tries to detect the indentation and falls back to a default if it can't
  let indent = (cov_16lcdpz3tp().s[3]++, (cov_16lcdpz3tp().b[0][0]++, (0, _detectIndent.default)(packageJsonString).indent) || (cov_16lcdpz3tp().b[0][1]++, '  '));
  let packageJsonContent = (cov_16lcdpz3tp().s[4]++, JSON.parse(packageJsonString));
  let newPackageJsonContent = (cov_16lcdpz3tp().s[5]++, '');
  cov_16lcdpz3tp().s[6]++;
  if (_lodash.default.get(packageJsonContent, 'config.commitizen.path') !== adapterNpmName) {
    cov_16lcdpz3tp().b[1][0]++;
    cov_16lcdpz3tp().s[7]++;
    newPackageJsonContent = _lodash.default.merge(packageJsonContent, commitizenAdapterConfig);
  } else {
    cov_16lcdpz3tp().b[1][1]++;
  }
  cov_16lcdpz3tp().s[8]++;
  _fs.default.writeFileSync(packageJsonPath, JSON.stringify(newPackageJsonContent, null, indent) + '\n');
}

/*
 * Get additional options for install command
 */
function getInstallOptions(stringMappings) {
  cov_16lcdpz3tp().f[1]++;
  cov_16lcdpz3tp().s[9]++;
  return Array.from(stringMappings.values()).filter(Boolean).join(" ");
}

/*
 * Get specific install command for passed package manager
 */
function getInstallCommand(packageManager) {
  cov_16lcdpz3tp().f[2]++;
  const fallbackCommand = (cov_16lcdpz3tp().s[10]++, 'install');
  const commandByPackageManager = (cov_16lcdpz3tp().s[11]++, {
    npm: 'install',
    yarn: 'add',
    pnpm: 'add'
  });
  cov_16lcdpz3tp().s[12]++;
  return (cov_16lcdpz3tp().b[2][0]++, commandByPackageManager[packageManager]) || (cov_16lcdpz3tp().b[2][1]++, fallbackCommand);
}

/**
 * Generates an npm install command given a map of strings and a package name
 */
function generateInstallAdapterCommand(stringMappings, adapterNpmName, packageManager = (cov_16lcdpz3tp().b[3][0]++, "npm")) {
  cov_16lcdpz3tp().f[3]++;
  cov_16lcdpz3tp().s[13]++;
  return `${packageManager} ${getInstallCommand(packageManager)} ${adapterNpmName} ${getInstallOptions(stringMappings)}`;
}

/**
 * Gets the nearest npm_modules directory
 */
function getNearestNodeModulesDirectory(options) {
  cov_16lcdpz3tp().f[4]++;
  // Get the nearest node_modules directories to the current working directory
  let nodeModulesDirectories = (cov_16lcdpz3tp().s[14]++, (0, _findNodeModules.default)(options));

  // Make sure we find a node_modules folder

  /* istanbul ignore else */
  cov_16lcdpz3tp().s[15]++;
  if ((cov_16lcdpz3tp().b[5][0]++, nodeModulesDirectories) && (cov_16lcdpz3tp().b[5][1]++, nodeModulesDirectories.length > 0)) {
    cov_16lcdpz3tp().b[4][0]++;
    cov_16lcdpz3tp().s[16]++;
    return nodeModulesDirectories[0];
  } else {
    console.error(`Error: Could not locate node_modules in your project's root directory. Did you forget to npm init or npm install?`);
  }
}

/**
 * Gets the nearest project root directory
 */
function getNearestProjectRootDirectory(repoPath, options) {
  cov_16lcdpz3tp().f[5]++;
  cov_16lcdpz3tp().s[17]++;
  return _path.default.join(repoPath, getNearestNodeModulesDirectory(options), '/../');
}

/**
 * Gets a map of arguments where the value is the corresponding (to passed package manager) string
 */
function getInstallStringMappings({
  save,
  dev,
  saveDev,
  exact,
  saveExact,
  force
}, packageManager) {
  cov_16lcdpz3tp().f[6]++;
  const npm = (cov_16lcdpz3tp().s[18]++, new Map().set('save', (cov_16lcdpz3tp().b[7][0]++, save) && (cov_16lcdpz3tp().b[7][1]++, !saveDev) ? (cov_16lcdpz3tp().b[6][0]++, '--save') : (cov_16lcdpz3tp().b[6][1]++, undefined)).set('saveDev', saveDev ? (cov_16lcdpz3tp().b[8][0]++, '--save-dev') : (cov_16lcdpz3tp().b[8][1]++, undefined)).set('saveExact', saveExact ? (cov_16lcdpz3tp().b[9][0]++, '--save-exact') : (cov_16lcdpz3tp().b[9][1]++, undefined)).set('force', force ? (cov_16lcdpz3tp().b[10][0]++, '--force') : (cov_16lcdpz3tp().b[10][1]++, undefined)));
  const yarn = (cov_16lcdpz3tp().s[19]++, new Map().set('dev', dev ? (cov_16lcdpz3tp().b[11][0]++, '--dev') : (cov_16lcdpz3tp().b[11][1]++, undefined)).set('exact', exact ? (cov_16lcdpz3tp().b[12][0]++, '--exact') : (cov_16lcdpz3tp().b[12][1]++, undefined)).set('force', force ? (cov_16lcdpz3tp().b[13][0]++, '--force') : (cov_16lcdpz3tp().b[13][1]++, undefined)));
  const pnpm = (cov_16lcdpz3tp().s[20]++, new Map().set('save', (cov_16lcdpz3tp().b[15][0]++, save) && (cov_16lcdpz3tp().b[15][1]++, !saveDev) ? (cov_16lcdpz3tp().b[14][0]++, '--save-prod') : (cov_16lcdpz3tp().b[14][1]++, undefined)).set('dev', saveDev ? (cov_16lcdpz3tp().b[16][0]++, '--save-dev') : (cov_16lcdpz3tp().b[16][1]++, undefined)).set('exact', saveExact ? (cov_16lcdpz3tp().b[17][0]++, '--save-exact') : (cov_16lcdpz3tp().b[17][1]++, undefined)));
  const map = (cov_16lcdpz3tp().s[21]++, {
    npm,
    yarn,
    pnpm
  });
  cov_16lcdpz3tp().s[22]++;
  return (cov_16lcdpz3tp().b[18][0]++, map[packageManager]) || (cov_16lcdpz3tp().b[18][1]++, npm);
}

/**
 * Gets the prompter from an adapter given an adapter path
 */
function getPrompter(adapterPath) {
  cov_16lcdpz3tp().f[7]++;
  // Resolve the adapter path
  let resolvedAdapterPath = (cov_16lcdpz3tp().s[23]++, resolveAdapterPath(adapterPath));

  // Load the adapter
  let adapter = (cov_16lcdpz3tp().s[24]++, require(resolvedAdapterPath));

  /* istanbul ignore next */
  if (adapter && adapter.prompter && (0, _util.isFunction)(adapter.prompter)) {
    return adapter.prompter;
  } else if (adapter && adapter.default && adapter.default.prompter && (0, _util.isFunction)(adapter.default.prompter)) {
    return adapter.default.prompter;
  } else {
    throw new Error(`Could not find prompter method in the provided adapter module: ${adapterPath}`);
  }
}

/**
 * Given a resolvable module name or path, which can be a directory or file, will
 * return a located adapter path or will throw.
 */
function resolveAdapterPath(inboundAdapterPath) {
  cov_16lcdpz3tp().f[8]++;
  // Check if inboundAdapterPath is a path or node module name
  let parsed = (cov_16lcdpz3tp().s[25]++, _path.default.parse(inboundAdapterPath));
  let isPath = (cov_16lcdpz3tp().s[26]++, (cov_16lcdpz3tp().b[19][0]++, parsed.dir.length > 0) && (cov_16lcdpz3tp().b[19][1]++, parsed.dir.charAt(0) !== "@"));

  // Resolve from the root of the git repo if inboundAdapterPath is a path
  let absoluteAdapterPath = (cov_16lcdpz3tp().s[27]++, isPath ? (cov_16lcdpz3tp().b[20][0]++, _path.default.resolve(getGitRootPath(), inboundAdapterPath)) : (cov_16lcdpz3tp().b[20][1]++, inboundAdapterPath));
  cov_16lcdpz3tp().s[28]++;
  try {
    cov_16lcdpz3tp().s[29]++;
    // try to resolve the given path
    return require.resolve(absoluteAdapterPath);
  } catch (error) {
    cov_16lcdpz3tp().s[30]++;
    error.message = "Could not resolve " + absoluteAdapterPath + ". " + error.message;
    cov_16lcdpz3tp().s[31]++;
    throw error;
  }
}
function getGitRootPath() {
  cov_16lcdpz3tp().f[9]++;
  cov_16lcdpz3tp().s[32]++;
  return _child_process.default.spawnSync('git', ['rev-parse', '--show-toplevel'], {
    encoding: 'utf8'
  }).stdout.trim();
}