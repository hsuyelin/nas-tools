const readConfigFile = require('../lib/read-config-file');
const log = require('../lib/logger');

jest.mock('find-config');
jest.mock('../lib/logger', () => ({
  error: jest.fn(),
}));

// This is a unit test but it reads real a config file in te project root.
// It could be called "integration". The most important is it increase our confidence.
it('logs message when config is not found', () => {
  const config = readConfigFile();
  expect(config).toEqual(null);
  expect(log.error).toHaveBeenCalledWith(
    'Unable to find a configuration file. Please refer to documentation to learn how to set up: https://github.com/leonardoanalista/cz-customizable#steps "',
  );
});
