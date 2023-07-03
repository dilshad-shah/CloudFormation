module.exports = {
  extends: ['nucleus/strict'],
  overrides: [
    {
      files: ['**/*.ts'],
      extends: ['nucleus/cdk']
    }
  ]
};
