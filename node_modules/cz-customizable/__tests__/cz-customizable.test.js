const czModule = require('../index');
const readConfigFile = require('../lib/read-config-file');
const getPreviousCommit = require('../lib/utils/get-previous-commit');

const commit = jest.fn();

jest.mock('./../lib/read-config-file');
jest.mock('./../lib/utils/get-previous-commit');

beforeEach(() => {
  const defaultConfig = {
    types: [
      { value: 'feat', name: 'feat:     A new feature' },
      { value: 'fix', name: 'fix:      A bug fix' },
      { value: 'docs', name: 'docs:     Documentation only changes' },
      {
        value: 'style',
        name:
          'style:    Changes that do not affect the meaning of the code\n' +
          '            (white-space, formatting, missing semi-colons, etc)',
      },
      {
        value: 'refactor',
        name: 'refactor: A code change that neither fixes a bug nor adds a feature',
      },
      {
        value: 'perf',
        name: 'perf:     A code change that improves performance',
      },
      { value: 'test', name: 'test:     Adding missing tests' },
      {
        value: 'chore',
        name:
          'chore:    Changes to the build process or auxiliary tools\n' +
          '            and libraries such as documentation generation',
      },
      { value: 'revert', name: 'revert:   Revert to a commit' },
      { value: 'WIP', name: 'WIP:      Work in progress' },
    ],
    scopes: [{ name: 'accounts' }, { name: 'admin' }, { name: 'exampleScope' }, { name: 'changeMe' }],
    allowTicketNumber: false,
    isTicketNumberRequired: false,
    ticketNumberPrefix: 'TICKET-',
    ticketNumberRegExp: '\\d{1,5}',
    messages: {
      type: "Select the type of change that you're committing:",
      scope: '\nDenote the SCOPE of this change (optional):',
      customScope: 'Denote the SCOPE of this change:',
      subject: 'Write a SHORT, IMPERATIVE tense description of the change:\n',
      body: 'Provide a LONGER description of the change (optional). Use "|" to break new line:\n',
      breaking: 'List any BREAKING CHANGES (optional):\n',
      footer: 'List any ISSUES CLOSED by this change (optional). E.g.: #31, #34:\n',
      confirmCommit: 'Are you sure you want to proceed with the commit above?',
    },
    allowCustomScopes: true,
    allowBreakingChanges: ['feat', 'fix'],
    skipQuestions: ['body'],
    subjectLimit: 100,
  };
  readConfigFile.mockReturnValue(defaultConfig);
});

describe('cz-customizable', () => {
  function getMockedCz(answers) {
    return {
      prompt() {
        return {
          then(cb) {
            cb(answers);
          },
        };
      },
    };
  }

  it('should commit without confirmation', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      subject: 'do it all',
    };

    const mockCz = getMockedCz(answers);

    // run commitizen plugin
    czModule.prompter(mockCz, commit);

    expect(commit).toHaveBeenCalledWith('feat: do it all');
  });

  it('should escape special characters sush as backticks', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      subject: 'with backticks `here`',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    expect(commit).toHaveBeenCalledWith('feat: with backticks \\`here\\`');
  });

  it('should not call commit() function if there is no final confirmation and display log message saying commit has been canceled', () => {
    const mockCz = getMockedCz({});

    // run commitizen plugin
    czModule.prompter(mockCz, commit);

    expect(commit).not.toHaveBeenCalled();
  });

  it('should call commit() function with commit message when user confirms commit and split body when pipes are present', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
      body: '-line1|-line2',
      breaking: 'breaking',
      footer: 'my footer',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    expect(commit).toHaveBeenCalledWith(
      'feat(myScope): create a new cool feature\n\n-line1\n-line2\n\nBREAKING CHANGE:\nbreaking\n\nISSUES CLOSED: my footer',
    );
  });

  it('should call commit() function with commit message with the minimal required fields', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);
    expect(commit).toHaveBeenCalledWith('feat(myScope): create a new cool feature');
  });

  it('should suppress scope when commit type is WIP', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'WIP',
      subject: 'this is my work-in-progress',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);
    expect(commit).toHaveBeenCalledWith('WIP: this is my work-in-progress');
  });

  it('should allow edit message before commit', (done) => {
    process.env.EDITOR = 'true';

    const answers = {
      confirmCommit: 'edit',
      type: 'feat',
      subject: 'create a new cool feature',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    setTimeout(() => {
      expect(commit).toHaveBeenCalledWith('feat: create a new cool feature');
      done();
    }, 100);
  });

  it('should not commit if editor returned non-zero value', (done) => {
    process.env.EDITOR = 'false';

    const answers = {
      confirmCommit: 'edit',
      type: 'feat',
      subject: 'create a new cool feature',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    setTimeout(() => {
      expect(commit).toHaveBeenCalledTimes(0);
      done();
    }, 100);
  });

  it('should truncate subject if number of characters is higher than 100', () => {
    const chars100 =
      '0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789';

    // this string will be prepend: "ISSUES CLOSED: " = 15 chars
    const footerChars100 =
      '0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-012345';

    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: chars100,
      body: `${chars100} body-second-line`,
      footer: `${footerChars100} footer-second-line`,
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    const firstPart = 'feat(myScope): ';

    expect(commit.mock.calls[0][0]).toMatchInlineSnapshot(`
      "${firstPart + answers.subject.slice(0, 100)}

      0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789
      body-second-line

      ISSUES CLOSED: 0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-0123456789-012345
      footer-second-line"
    `);
  });

  it('should call commit() function with custom breaking prefix', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
      breaking: 'breaking',
      footer: 'my footer',
    };

    readConfigFile.mockReturnValue({
      types: [{ value: 'feat', name: 'feat: my feat' }],
      scopes: [{ name: 'myScope' }],
      scopeOverrides: {
        fix: [{ name: 'fixOverride' }],
      },
      allowCustomScopes: true,
      allowBreakingChanges: ['feat'],
      breakingPrefix: 'WARNING:',
    });

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    expect(commit).toHaveBeenCalledWith(
      'feat(myScope): create a new cool feature\n\nWARNING:\nbreaking\n\nISSUES CLOSED: my footer',
    );
  });

  it('should call commit() function with custom footer prefix', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
      breaking: 'breaking',
      footer: 'my footer',
    };

    readConfigFile.mockReturnValue({
      types: [{ value: 'feat', name: 'feat: my feat' }],
      scopes: [{ name: 'myScope' }],
      scopeOverrides: {
        fix: [{ name: 'fixOverride' }],
      },
      allowCustomScopes: true,
      allowBreakingChanges: ['feat'],
      footerPrefix: 'FIXES:',
    });

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    expect(commit).toHaveBeenCalledWith(
      'feat(myScope): create a new cool feature\n\nBREAKING CHANGE:\nbreaking\n\nFIXES: my footer',
    );
  });

  it('should call commit() function with custom footer prefix set to empty string', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
      breaking: 'breaking',
      footer: 'my footer',
    };

    readConfigFile.mockReturnValue({
      types: [{ value: 'feat', name: 'feat: my feat' }],
      scopes: [{ name: 'myScope' }],
      scopeOverrides: {
        fix: [{ name: 'fixOverride' }],
      },
      allowCustomScopes: true,
      allowBreakingChanges: ['feat'],
      footerPrefix: '',
    });

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);

    expect(commit).toHaveBeenCalledWith(
      'feat(myScope): create a new cool feature\n\nBREAKING CHANGE:\nbreaking\n\nmy footer',
    );
  });

  it('should call commit() function with ticket number', () => {
    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
      ticketNumber: 'TICKET-1234',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);
    expect(commit).toHaveBeenCalledWith('feat(myScope): TICKET-TICKET-1234 create a new cool feature');
  });

  it('should call commit() function with ticket number and prefix', () => {
    readConfigFile.mockReturnValue({
      types: [{ value: 'feat', name: 'feat: my feat' }],
      scopes: [{ name: 'myScope' }],
      scopeOverrides: {
        fix: [{ name: 'fixOverride' }],
      },
      allowCustomScopes: true,
      allowBreakingChanges: ['feat'],
      breakingPrefix: 'WARNING:',
      ticketNumberPrefix: 'TICKET-',
    });

    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
      ticketNumber: '1234',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);
    expect(commit).toHaveBeenCalledWith('feat(myScope): TICKET-1234 create a new cool feature');
  });

  it('should call commit() function with preparedCommit message', () => {
    getPreviousCommit.mockReturnValue('fix: a terrible bug');

    readConfigFile.mockReturnValue({
      types: [{ value: 'feat', name: 'feat: my feat' }],
      scopes: [{ name: 'myScope' }],
      scopeOverrides: {
        fix: [{ name: 'fixOverride' }],
      },
      allowCustomScopes: true,
      allowBreakingChanges: ['feat'],
      usePreparedCommit: true,
    });

    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      subject: 'create a new cool feature',
    };

    const mockCz = getMockedCz(answers);
    czModule.prompter(mockCz, commit);
    expect(commit).toHaveBeenCalledWith('feat: create a new cool feature');
  });
});
