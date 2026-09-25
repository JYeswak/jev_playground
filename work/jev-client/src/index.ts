/**
 * Re-export restored (pane 1, CI red at b54ffc47). The K7 migration moved only the omp tools
 * and gate hook. About 104 files under work/, demos/ and scripts/ still import this path.
 * Remove this re-export only once a grep for "jev-client/src/index" finds no importers.
 */
export * from "../../../kit/src/client.ts";
