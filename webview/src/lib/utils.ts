import region from "$locales/region_zh.json";
import style from "$locales/style_zh.json";
import tone from "$locales/tone_zh.json";
import cooperation from "$locales/cooperation_zh.json";
import grow from "$locales/grow_zh.json";
import position from "$locales/position_zh.json";
import rank from "$locales/rank_zh.json";
import ability from "$locales/ability_zh.json";

export function toHex(num: number | undefined): string {
    return num !== undefined ? num.toString(16).padStart(2, '0').toUpperCase() : "";
}

export function fromHex(hexString: string): number {
    return parseInt(hexString, 16);
}

function lookup(dict: Record<string, string>, num: number | undefined): string {
    return num !== undefined ? dict[toHex(num)] ?? "" : "";
}

export const getRegion = (num: number | undefined) => lookup(region, num);
export const getStyle = (num: number | undefined) => lookup(style, num);
export const getToneType = (num: number | undefined) => lookup(tone, num);
export const getCooperationType = (num: number | undefined) => lookup(cooperation, num);
export const getGrowType = (num: number | undefined) => lookup(grow, num);
export const getPosition = (num: number | undefined) => lookup(position, num);
export const getRank = (num: number | undefined) => lookup(rank, num);

export function preferFoot(footValue: number | undefined): string {
    if (footValue === 0) {
        return '左脚';
    } else if (footValue === 1) {
        return '右脚';
    } else {
        return '双脚';
    }
}

export const sortedRegion = Object.entries(region).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedStyle = Object.entries(style).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedToneType = Object.entries(tone).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedCooperationType = Object.entries(cooperation).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedGrowType = Object.entries(grow).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedPosition = Object.entries(position).sort((a, b) => a[0].localeCompare(b[0]));
export const sortedAbilities = ability;
