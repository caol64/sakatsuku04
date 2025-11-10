<script lang="ts">
    import type { BCoach } from "$lib/models";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import {
        getAcPracData,
        getMcoachSkillData,
        getRank,
        getRegion,
        getStyle,
        getTeamData,
        toHex,
    } from "$lib/utils";
    import ability from "$locales/mcoach_abilities_zh.json";
    import AbilityBar from "./AbilityBar.svelte";
    import RadarChart6 from "./RadarChart6.svelte";
    import activatePlan from "$locales/activate_plan_zh.json";
    import trainingPlan from "$locales/training_plan_zh.json";
    import trainingStrength from "$locales/training_strength_zh.json";
    import coachType from "$locales/coach_type_zh.json";
    import Component from "$lib/icons/Component.svelte";
    import Airplane from "$lib/icons/Airplane.svelte";

    let { selectedCoach = 0, age }: { selectedCoach: number; age?: number } = $props();

    let bCoach: BCoach = $state({ abilities: [], hexagon: [] });
    let stats = $state(Array(6).fill(0));

    let abilityPairs = $derived(
        ability.map((label, i) => ({
            label,
            value: [0, 0, bCoach.abilities[i]],
        })),
    );

    async function fetchBCoach() {
        if (selectedCoach >= 20000) {
            if (window.pywebview?.api?.get_bcoach) {
                bCoach = await window.pywebview.api.get_bcoach(selectedCoach);
                stats = bCoach.hexagon;
                if (age !== undefined && age > 0) {
                    bCoach.age = age;
                }
            } else {
                alert("API 未加载");
            }
        }
    }

    $effect(() => {
        if (selectedCoach) {
            fetchBCoach();
        }
    });
</script>

<VStack className="w-1/5 mx-1">
    <div
        class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700"
    >
        <p class="flex items-center justify-between">
            姓名
            <span class="flex-1 pl-8 text-sm select-text">{bCoach?.name}</span>
        </p>
        <p>
            ID
            <span class="pl-8 text-sm select-text">{toHex(bCoach?.id, 4)}</span>
        </p>
        <p>
            出生地
            <span class="pl-8 text-sm">{getRegion(bCoach?.born)}</span>
        </p>
        <p>
            年龄
            <span class="pl-8 text-sm">{bCoach?.age}</span>
        </p>
        <p>
            年薪
            {#if bCoach?.salaryHigh}
                <span class="pl-8 text-sm">
                    {bCoach?.salaryHigh} 亿
                </span>
            {/if}
            <span class="pl-{bCoach?.salaryHigh ? '2' : '8'} text-sm"
                >{bCoach?.salaryLow} 万</span
            >
        </p>
        <p>
            等级
            <span class="pl-8 text-sm">{getRank(bCoach?.rank)}</span>
        </p>
        <p>
            出现所需声望
            <span class="pl-5 text-sm">{bCoach?.signingDifficulty}</span>
        </p>
        <p>隐藏属性</p>
        <div class="pl-4 grid grid-cols-2 gap-x-1 text-sm text-left">
            <div>
                <span>野心</span><span class="pl-3">{bCoach?.ambition}</span>
            </div>
            <div>
                <span>毅力</span><span class="pl-3">{bCoach?.persistence}</span>
            </div>
            <div>
                <span>欲望</span><span class="pl-3">{bCoach?.desire}</span>
            </div>
        </div>
        <p>启用方针</p>
        <div class="pl-4 text-sm text-left">
            {bCoach?.activatePlan !== undefined
                ? activatePlan[bCoach.activatePlan]
                : ""}
        </div>
        <p>练习方针</p>
        <div class="pl-4 text-sm text-left">
            {bCoach?.trainingPlan !== undefined
                ? trainingPlan[bCoach.trainingPlan]
                : ""}·{bCoach?.trainingStrength !== undefined
                ? trainingStrength[bCoach.trainingStrength]
                : ""}
        </div>
        <p>固有风格</p>
        <div class="pl-4 text-sm text-left">
            {#if bCoach?.styles && bCoach.styles.length > 0}
                {#each bCoach.styles as item}
                    {#if item > 0}
                        <div>{getStyle(item)}</div>
                    {/if}
                {/each}
            {/if}
        </div>
        {#if bCoach?.spSkill !== undefined && bCoach?.spSkill !== null}
            <div class="flex items-center gap-x-2">
                <p>特殊战术</p>
                <Component />
            </div>
            <div class="pl-4 text-sm text-left">
                {getMcoachSkillData()[bCoach.spSkill]}
            </div>
        {/if}
        {#if bCoach.bringAbroads && bCoach.bringAbroads.length > 0}
            <div class="flex items-center gap-x-2">
                <p>留学/集训地</p>
                <Airplane />
            </div>
            <div class="pl-4 text-sm text-left">
                {#each bCoach.bringAbroads as abr}
                    <div>{`${getTeamData()[abr.id - 255]}${abr.type === 1 ? " [集训地]" : " [留学地]"}`}</div>
                {/each}
            </div>
        {/if}
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    <RadarChart6 abilities={stats} />
    <div
        class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2"
    >
        <p>{bCoach?.eval}</p>
    </div>
    <div
        class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2"
    >
        <p>以助教身份出现时类型</p>
        <div class="pl-4 text-sm text-left">
            {bCoach?.coachTypeCnv !== undefined
                ? coachType[bCoach.coachTypeCnv]
                : ""}
        </div>
        <p>助教特训</p>
        <div class="pl-4 text-sm text-left">
            {#if bCoach?.acSpPractice1 !== undefined}
                <div>{getAcPracData()[bCoach.acSpPractice1]}</div>
            {/if}
            {#if bCoach?.acSpPractice2}
                <div>{getAcPracData()[bCoach.acSpPractice2]}</div>
            {/if}
        </div>
    </div>
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-50 text-sm">{label}</span>
            {#if value}
                {@const tooltipText = `${value[2]}`}
                <Tooltip text={tooltipText} className="w-full">
                    <AbilityBar abilities={value} is100={true} />
                </Tooltip>
            {/if}
        </HStack>
    {/each}
</VStack>
