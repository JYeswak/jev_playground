// PokéJev local format: the fork's "Gen 9 OU" (config/formats.ts @e64915c0e) with its AI-tournament
// clock (600 s bank, 60 s grace, 150 s per turn) replaced by a clock no looser than either the
// Showdown ladder (server/room-battle.ts: 150 s bank, 60 s grace, +10 s per turn, 150 s per turn) or
// the PokéChamp paper's statement of it (150 s per game, 15 s per turn increment, losing on either):
// a 150 s bank, 15 s added per turn and capped at the bank, no more than 15 s for any single decision,
// and effectively no grace. The server's config.js already sets forcetimer = true, so the timer runs in
// every battle without either player asking for it.
// Copied into pokemon-showdown/config/ by work/poke-jev/serve.sh (an untracked file in the clone).

import type {FormatList} from '../sim/dex-formats';

export const Formats: FormatList = [
	{
		section: "PokéJev",
	},
	{
		name: "Gen 9 OU Clock",
		mod: 'gen9',
		ruleset: [
			'Standard', 'Evasion Abilities Clause', 'Sleep Moves Clause', '!Sleep Clause Mod',
			'Timer Starting = 150', 'Timer Grace = 1', 'Timer Add Per Turn = 15',
			'Timer Max Per Turn = 15', 'Timer Max First Turn = 15',
		],
		banlist: ['Uber', 'AG', 'Arena Trap', 'Moody', 'Shadow Tag', 'King\'s Rock', 'Razor Fang', 'Baton Pass', 'Last Respects', 'Shed Tail', 'Zoroark', 'Revival Blessing', 'Zorua'],
	},
];
