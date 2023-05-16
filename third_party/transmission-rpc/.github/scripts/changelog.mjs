import conventionalChangelog from 'conventional-changelog';

const commitTemplate = `*{{#if scope}} **{{scope}}**:
{{~/if}} {{#if subject}}
  {{~subject}}
{{~else}}
  {{~header}}
{{~/if}}

`;

const s = conventionalChangelog(
  {
    preset: 'conventionalcommits',
    tagPrefix: 'v',
    releaseCount: 2,
  },
  { linkReferences: false },
  undefined,
  {
    noteKeywords: ['BREAKING CHANGE'],
  },
  {
    headerPartial: '',
    commitPartial: commitTemplate,
    transform(commit) {
      if (!commit.type) {
        return false;
      }

      if (!['feat', 'fix', 'perf', 'revert', 'refactor'].includes(commit.type)) {
        return false;
      }

      if (commit.type === 'refactor') {
        if (!commit.notes.length) {
          return false;
        }
      }

      if (commit.type === 'feat') {
        commit.type = 'Features';
      } else if (commit.type === 'fix') {
        commit.type = 'Bug Fixes';
      } else if (commit.type === 'perf') {
        commit.type = 'Performance Improvements';
      } else if (commit.type === 'revert' || commit.revert) {
        commit.type = 'Reverts';
      }

      commit.references = [];

      return commit;
    },
  },
);

let changelog = '';

s.on('data', function (data) {
  changelog += data.toString();
});

s.on('end', function () {
  changelog = changelog
    .split('\n')
    .map((value) => value.trim())
    .join('\n')
    .trim();

  console.log(changelog);
});
