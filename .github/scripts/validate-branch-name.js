const { execFileSync } = require("node:child_process");

const branch = execFileSync("git", ["symbolic-ref", "--short", "HEAD"], {
  encoding: "utf8",
}).trim();

if (["main", "stg", "develop"].includes(branch)) {
  process.exit(0);
}

const pattern =
  /^(feat|fix|hotfix|refactor|chore|docs|test|style|perf|ci|build)\/[A-Z][A-Z0-9]*-[0-9]+_[a-z0-9][a-z0-9-]*$/;

if (!pattern.test(branch)) {
  console.error(`Branch '${branch}' nao segue o padrao obrigatorio:`);
  console.error("<tipo>/<JIRA-TICKET>_titulo-do-ticket");
  console.error(
    "Tipos validos: feat, fix, hotfix, refactor, chore, docs, test, style, perf, ci, build",
  );
  console.error("Exemplo: feat/FC404-42_criar-tela-de-login");
  process.exit(1);
}
