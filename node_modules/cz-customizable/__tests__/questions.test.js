const questions = require('../lib/questions');

describe('cz-customizable', () => {
  let config;

  beforeEach(() => {
    config = null;
  });

  const mockedCz = {
    Separator: jest.fn(),
  };

  const getQuestion = (number) => questions.getQuestions(config, mockedCz)[number - 1];

  it('should array of questions be returned', () => {
    config = {
      types: [{ value: 'feat', name: 'feat: my feat' }],
      scopes: [{ name: 'myScope' }],
      scopeOverrides: {
        fix: [{ name: 'fixOverride' }],
      },
      allowCustomScopes: true,
      allowBreakingChanges: ['feat'],
      allowTicketNumber: true,
      isTicketNumberRequired: true,
      ticketNumberPrefix: 'TICKET-',
      ticketNumberRegExp: '\\d{1,5}',
      subjectLimit: 40,
    };

    // question 1 - TYPE
    expect(getQuestion(1).name).toEqual('type');
    expect(getQuestion(1).type).toEqual('list');
    expect(getQuestion(1).choices[0]).toEqual({
      value: 'feat',
      name: 'feat: my feat',
    });

    // question 2 - SCOPE
    expect(getQuestion(2).name).toEqual('scope');
    expect(getQuestion(2).choices({})[0]).toEqual({ name: 'myScope' });
    expect(getQuestion(2).choices({ type: 'fix' })[0]).toEqual({
      name: 'fixOverride',
    }); // should override scope
    expect(getQuestion(2).when({ type: 'fix' })).toEqual(true);
    expect(getQuestion(2).when({ type: 'WIP' })).toEqual(false);
    expect(getQuestion(2).when({ type: 'wip' })).toEqual(false);

    // question 3 - SCOPE CUSTOM
    expect(getQuestion(3).name).toEqual('scope');
    expect(getQuestion(3).when({ scope: 'custom' })).toEqual(true);
    expect(getQuestion(3).when({ scope: false })).toEqual(false);
    expect(getQuestion(3).when({ scope: 'scope' })).toEqual(false);

    // question 4 - TICKET_NUMBER
    expect(getQuestion(4).name).toEqual('ticketNumber');
    expect(getQuestion(4).type).toEqual('input');
    expect(getQuestion(4).message.indexOf('Enter the ticket number following this pattern')).toEqual(0);
    expect(getQuestion(4).validate()).toEqual(false); // mandatory question

    // question 5 - SUBJECT
    expect(getQuestion(5).name).toEqual('subject');
    expect(getQuestion(5).type).toEqual('input');
    // expect(getQuestion(5).default).toEqual(null);
    expect(getQuestion(5).message).toMatch(/IMPERATIVE tense description/);
    expect(getQuestion(5).filter('Subject')).toEqual('subject');
    expect(getQuestion(5).validate('bad subject that exceed limit for 6 characters')).toEqual('Exceed limit: 40');
    expect(getQuestion(5).validate('good subject')).toEqual(true);

    // question 6 - BODY
    expect(getQuestion(6).name).toEqual('body');
    expect(getQuestion(6).type).toEqual('input');
    // expect(getQuestion(6).default).toEqual(null);

    // question 7 - BREAKING CHANGE
    expect(getQuestion(7).name).toEqual('breaking');
    expect(getQuestion(7).type).toEqual('input');
    expect(getQuestion(7).when({ type: 'feat' })).toEqual(true);
    expect(getQuestion(7).when({ type: 'fix' })).toEqual(false);

    // question 8 - FOOTER
    expect(getQuestion(8).name).toEqual('footer');
    expect(getQuestion(8).type).toEqual('input');
    expect(getQuestion(8).when({ type: 'fix' })).toEqual(true);
    expect(getQuestion(8).when({ type: 'WIP' })).toEqual(false);

    // question 9, last one, CONFIRM COMMIT OR NOT
    expect(getQuestion(9).name).toEqual('confirmCommit');
    expect(getQuestion(9).type).toEqual('expand');

    const answers = {
      confirmCommit: 'yes',
      type: 'feat',
      scope: 'myScope',
      subject: 'create a new cool feature',
    };
    expect(getQuestion(9).message(answers)).toMatch('Are you sure you want to proceed with the commit above?');
  });

  it('default length limit of subject should be 100', () => {
    config = {
      types: [{ value: 'feat', name: 'feat: my feat' }],
    };
    expect(getQuestion(5).validate('good subject')).toEqual(true);
    expect(
      getQuestion(5).validate(
        'bad subject that exceed limit bad subject that exceed limitbad subject that exceed limit test test test',
      ),
    ).toEqual('Exceed limit: 100');
  });

  it('subject should be lowercased by default', () => {
    config = {};
    expect(getQuestion(5).filter('Some subject')).toEqual('some subject');
  });

  it('subject should be capitilized when config property "upperCaseSubject" is set to true', () => {
    config = {
      upperCaseSubject: true,
    };

    expect(getQuestion(5).filter('some subject')).toEqual('Some subject');
  });

  describe('optional fixOverride and allowBreakingChanges', () => {
    it('should restrict BREAKING CHANGE question when config property "allowBreakingChanges" specifies array of types', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        scopes: [{ name: 'myScope' }],
        allowBreakingChanges: ['fix'],
      };
      expect(getQuestion(7).name).toEqual('breaking');

      const answers = {
        type: 'feat',
      };

      expect(getQuestion(7).when(answers)).toEqual(false); // not allowed
    });

    it('should allow BREAKING CHANGE question when config property "allowBreakingChanges" specifies array of types and answer is one of those', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        scopes: [{ name: 'myScope' }],
        allowBreakingChanges: ['fix', 'feat'],
      };
      expect(getQuestion(7).name).toEqual('breaking');

      const answers = {
        type: 'feat',
      };

      expect(getQuestion(7).when(answers)).toEqual(true); // allowed
    });
  });

  describe('Optional scopes', () => {
    it('should use scope override', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        scopeOverrides: {
          feat: [{ name: 'myScope' }],
        },
      };

      // question 2 with
      expect(getQuestion(2).name).toEqual('scope');
      expect(getQuestion(2).choices({})[0]).toBeUndefined();
      expect(getQuestion(2).choices({ type: 'feat' })[0]).toEqual({
        name: 'myScope',
      }); // should override scope
      expect(getQuestion(2).when({ type: 'feat' })).toEqual(true);

      const answers = { type: 'fix' };
      expect(getQuestion(2).when(answers)).toEqual(false);
      expect(answers.scope).toEqual('custom');
    });
  });

  describe('no TicketNumber question', () => {
    it('should use scope override', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        allowTicketNumber: false,
      };

      expect(getQuestion(4).name).toEqual('ticketNumber');
      expect(getQuestion(4).when()).toEqual(false);
    });
  });

  describe('ask for breaking change first', () => {
    it('when config askForBreakingChangeFirst is true', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        askForBreakingChangeFirst: true,
      };

      expect(getQuestion(1).name).toEqual('breaking');
      expect(getQuestion(1).when()).toEqual(true);
    });
  });

  describe('TicketNumber', () => {
    it('disable TicketNumber question', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        allowTicketNumber: false,
      };

      expect(getQuestion(4).name).toEqual('ticketNumber');
      expect(getQuestion(4).when()).toEqual(false);
    });

    it('custom message defined', () => {
      config = {
        types: [{ value: 'feat', name: 'feat: my feat' }],
        allowTicketNumber: true,
        messages: {
          ticketNumber: 'ticket number',
        },
      };

      expect(getQuestion(4).name).toEqual('ticketNumber');
      expect(getQuestion(4).message).toEqual('ticket number');
    });

    describe('validation', () => {
      it('invalid because empty and required', () => {
        config = {
          isTicketNumberRequired: true,
        };
        expect(getQuestion(4).validate('')).toEqual(false);
      });
      it('empty but valid because optional', () => {
        config = {
          isTicketNumberRequired: false,
        };
        expect(getQuestion(4).validate('')).toEqual(true);
      });
      it('valid because there is no regexp defined', () => {
        config = {
          isTicketNumberRequired: true,
          ticketNumberRegExp: undefined,
        };
        expect(getQuestion(4).validate('21234')).toEqual(true);
      });
      it("invalid because regexp don't match", () => {
        config = {
          isTicketNumberRequired: true,
          ticketNumberRegExp: '\\d{1,5}',
        };
        expect(getQuestion(4).validate('sddsa')).toEqual(false);
      });
      it('valid because regexp match', () => {
        config = {
          isTicketNumberRequired: true,
          ticketNumberRegExp: '\\d{1,5}',
        };
        expect(getQuestion(4).validate('12345')).toEqual(true);
      });
    });
  });
});
