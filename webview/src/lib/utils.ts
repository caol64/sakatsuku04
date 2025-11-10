import { gameVersion } from "$lib/globalState.svelte";

import position from "$locales/position_zh.json";
import rank from "$locales/rank_zh.json";
import teamZh from "$locales/teams_zh.json";
import teamJp from "$locales/teams_jp.json";
import sponsorsZh from "$locales/sponsor_zh.json";
import sponsorsJp from "$locales/sponsor_jp.json";
import styleZh from "$locales/style_zh.json";
import styleJp from "$locales/style_jp.json";
import growEvalZh from "$locales/grow_eval_zh.json";
import growEvalJp from "$locales/grow_eval_jp.json";
import abilEvalZh from "$locales/abil_eval_zh.json";
import abilEvalJp from "$locales/abil_eval_jp.json";
import toneZh from "$locales/tone_zh.json";
import toneJp from "$locales/tone_jp.json";
import abilityZh from "$locales/ability_zh.json";
import abilityJp from "$locales/ability_jp.json";
import acPracZh from "$locales/ac_prac_zh.json";
import acPracJp from "$locales/ac_prac_jp.json";
import cooperationZh from "$locales/cooperation_zh.json";
import cooperationJp from "$locales/cooperation_jp.json";
import growZh from "$locales/grow_zh.json";
import growJp from "$locales/grow_jp.json";
import regionZh from "$locales/region_zh.json";
import regionJp from "$locales/region_jp.json";
import footZh from "$locales/foot_zh.json";
import footJp from "$locales/foot_jp.json";
import mcoachSkillZh from "$locales/mcoach_skill_zh.json";
import mcoachSkillJp from "$locales/mcoach_skill_jp.json";

export function toHex(num: number | undefined, range: number = 2): string {
    return num !== undefined ? num.toString(16).padStart(range, '0').toUpperCase() : "";
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

export const getRegion = (num: number | undefined) => lookup(getRegionData(), num);
export const getFoot = (num: number | undefined) => lookup(getFootData(), num);
export const getStyle = (num: number | undefined) => lookup(getPlayStyleData(), num);
export const getToneType = (num: number | undefined) => lookup(getToneTypelData(), num);
export const getCooperationType = (num: number | undefined) => lookup(getCooperationlData(), num);
export const getGrowType = (num: number | undefined) => lookup(getGrowData(), num);
export const getPosition = (num: number | undefined) => num !== undefined ? position[num] : "";
export const getRank = (num: number | undefined) => lookup(rank, num);
export const getGrowEval = (num: number | undefined) => lookupDirect(getGrowEvalData(), num);

export const sortedRegion = Object.entries(getRegionData()).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedStyle = Object.entries(getPlayStyleData()).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedToneType = Object.entries(getToneTypelData()).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedCooperationType = Object.entries(getCooperationlData()).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedGrowType = Object.entries(getGrowData()).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedPosition = position;
export const sortedRank = Object.entries(rank).sort((a, b) => a[0].localeCompare(b[0]));

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

export function getTeamData(): string[] {
    return gameVersion === "zh" ? teamZh : teamJp;
}

export function getSponsorData(): string[] {
    return gameVersion === "zh" ? sponsorsZh : sponsorsJp;
}

export function getPlayStyleData(): Record<string, string> {
    return gameVersion === "zh" ? styleZh : styleJp;
}

export function getGrowEvalData(): Record<string, string> {
    return gameVersion === "zh" ? growEvalZh : growEvalJp;
}

export function getAbilEvalData(): string[] {
    return gameVersion === "zh" ? abilEvalZh : abilEvalJp;
}

export function getToneTypelData(): Record<string, string> {
    return gameVersion === "zh" ? toneZh : toneJp;
}

export function getAbilityData(): string[] {
    return gameVersion === "zh" ? abilityZh : abilityJp;
}

export function getAcPracData(): string[] {
    return gameVersion === "zh" ? acPracZh : acPracJp;
}

export function getCooperationlData(): Record<string, string> {
    return gameVersion === "zh" ? cooperationZh : cooperationJp;
}

export function getGrowData(): Record<string, string> {
    return gameVersion === "zh" ? growZh : growJp;
}

export function getRegionData(): Record<string, string> {
    return gameVersion === "zh" ? regionZh : regionJp;
}

export function getFootData(): Record<string, string> {
    return gameVersion === "zh" ? footZh : footJp;
}

export function getMcoachSkillData(): string[] {
    return gameVersion === "zh" ? mcoachSkillZh : mcoachSkillJp;
}
