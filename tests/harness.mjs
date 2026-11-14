// Runs an actions/github-script `script` against a fake GitHub API, the way the action would.
// stdin (JSON):  { script, context, env, existingLabels }
// stdout (JSON): { calls, failed, infos, summary }
import { readFileSync } from 'node:fs';

const input = JSON.parse(readFileSync(0, 'utf8'));
const existing = new Set((input.existingLabels || []).map((name) => name.toLowerCase()));
const calls = [];
const result = { failed: null, infos: [], summary: '' };

const notFound = () => Object.assign(new Error('Not Found'), { status: 404 });
const github = {
  rest: {
    issues: {
      async getLabel({ name }) {
        calls.push(['getLabel', name]);
        if (!existing.has(name.toLowerCase())) throw notFound();
        return { data: { name } };
      },
      async createLabel({ name, color, description }) {
        calls.push(['createLabel', name, color, description]);
        existing.add(name.toLowerCase());
        return { data: { name } };
      },
      async addLabels({ labels }) {
        calls.push(['addLabels', ...labels]);
        return { data: [] };
      },
      async removeLabel({ name }) {
        calls.push(['removeLabel', name]);
        return { data: [] };
      },
    },
  },
};

// Only the parts of @actions/core the scripts use; anything else throws and fails the test.
const summary = {
  addHeading(text) { result.summary += `## ${text}\n`; return summary; },
  addList(items) { result.summary += items.map((item) => `- ${item}\n`).join(''); return summary; },
  async write() { return summary; },
};
const core = {
  info: (message) => result.infos.push(String(message)),
  setFailed: (message) => { result.failed = String(message); },
  summary,
};

Object.assign(process.env, input.env || {});
const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor;
await new AsyncFunction('github', 'context', 'core', input.script)(github, input.context, core);
process.stdout.write(JSON.stringify({ calls, ...result }));
