module.exports = {
  extends: ['@commitlint/config-conventional'],
  plugins: [
    {
      rules: {
        'jira-scope': ({ scope }) => {
          const valid = /^[A-Z][A-Z0-9]*-\d+$/.test(scope ?? '');
          return [valid, 'O escopo deve ser um ticket Jira valido (ex: FC404-42)'];
        },
      },
    },
  ],
  rules: {
    'scope-empty': [2, 'never'],   // escopo obrigatorio
    'scope-case': [0],             // desativado — tickets Jira sao uppercase
    'jira-scope': [2, 'always'],   // valida padrao [A-Z]+-[0-9]+
  },
};
