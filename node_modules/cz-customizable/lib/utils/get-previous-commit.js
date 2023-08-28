const fs = require('fs');

const getPreparedCommit = (filePath = './.git/COMMIT_EDITMSG') => {
  if (fs.existsSync(filePath)) {
    return fs.readFileSync('./.git/COMMIT_EDITMSG', 'utf-8');
  }

  return null;
};

module.exports = getPreparedCommit;
