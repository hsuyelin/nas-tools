const readConfigFile = require('../lib/read-config-file');

const configInRootPackage = require('../.cz-config');
const configExampleInRootPackage = require('../cz-config-EXAMPLE');

// This is a unit test but it reads real a config file in te project root.
// It could be called "integration". The most important is it increase our confidence.
it('return config the nearest config in the root repo', () => {
  const config = readConfigFile();
  expect(config).toEqual(configInRootPackage);
});

it('return sample config when .cz-config.js does not exist in the repo root and user home directory', () => {
  const config = readConfigFile('.configNonExists');
  expect(config).toEqual(configExampleInRootPackage);
});
