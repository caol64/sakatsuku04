import region from "$locales/region_zh.json";
import foot from "$locales/foot_zh.json";
import style from "$locales/style_zh.json";
import tone from "$locales/tone_zh.json";
import cooperation from "$locales/cooperation_zh.json";
import grow from "$locales/grow_zh.json";
import position from "$locales/position_zh.json";
import rank from "$locales/rank_zh.json";
import ability from "$locales/ability_zh.json";
import growEval from "$locales/grow_eval_zh.json";

export function toHex(num: number | undefined): string {
    return num !== undefined ? num.toString(16).padStart(2, '0').toUpperCase() : "";
}

export function fromHex(hexString: string): number {
    return parseInt(hexString, 16);
}

function lookup(dict: Record<string, string>, num: number | undefined): string {
    return num !== undefined ? dict[toHex(num)] ?? "" : "";
}

function lookupDirect(dict: Record<string, string>, num: number | undefined): string {
    return num !== undefined ? dict[String(num)] ?? "" : "";
}

export const getRegion = (num: number | undefined) => lookup(region, num);
export const getFoot = (num: number | undefined) => lookup(foot, num);
export const getStyle = (num: number | undefined) => lookup(style, num);
export const getToneType = (num: number | undefined) => lookup(tone, num);
export const getCooperationType = (num: number | undefined) => lookup(cooperation, num);
export const getGrowType = (num: number | undefined) => lookup(grow, num);
export const getPosition = (num: number | undefined) => lookup(position, num);
export const getRank = (num: number | undefined) => lookup(rank, num);
export const getGrowEval = (num: number | undefined) => lookupDirect(growEval, num);

export const sortedRegion = Object.entries(region).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedStyle = Object.entries(style).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedToneType = Object.entries(tone).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedCooperationType = Object.entries(cooperation).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedGrowType = Object.entries(grow).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedPosition = Object.entries(position).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedRank = Object.entries(rank).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedAbilities = ability;

export function getPlayerColor(pos: number): string {
    switch (pos) {
        case 0: return "#f87171"; // red-400
        case 1: return "#60a5fa"; // blue-400
        case 2: return "#22d3ee"; // cyan-400
        case 3: return "#facc15"; // yellow-400
        case 4: return "#fde68a"; // yellow-200
        case 5: return "#fde68a"; // yellow-200
        case 6: return "#34d399"; // green-400
        case 7: return "#34d399"; // green-400
        default: return "#e5e7eb"; // gray-200 fallback
    }
}

export function debounce(
    func: (...args: any[]) => void,
    delay: number
): (...args: any[]) => void {
    let timeoutId: ReturnType<typeof setTimeout>;

    return function(this: any, ...args: any[]) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}
