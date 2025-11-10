<script lang="ts">
    import Airplane from "$lib/icons/Airplane.svelte";
    import Component from "$lib/icons/Component.svelte";
    import { type Coach } from "$lib/models";
    import { getAcPracData, getMcoachSkillData, getRank, getRegion, getStyle, getTeamData, toHex } from "$lib/utils";
    import AbilityBar from "./AbilityBar.svelte";
    import RadarChart6 from "./RadarChart6.svelte";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import ability from "$locales/mcoach_abilities_zh.json";
    import activatePlan from "$locales/activate_plan_zh.json";
    import trainingPlan from "$locales/training_plan_zh.json";
    import trainingStrength from "$locales/training_strength_zh.json";

    let { selectedCoach }: {selectedCoach: Coach} = $props();

    let abilityPairs = $derived(
        ability.map((label, i) => ({
            label,
            value: [0, 0, selectedCoach.abilities[i]]
        }))
    );

</script>

<VStack className="w-1/5 mx-1">
    <div
        class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700"
    >
        <p class="flex items-center justify-between">
            姓名
            <span class="flex-1 pl-8 text-sm select-text">{selectedCoach?.name}</span>
        </p>
        <p>
            ID
            <span class="pl-8 text-sm select-text">{selectedCoach?.id && toHex(selectedCoach.id, 4)}</span>
        </p>
        <p>
            出生地
            <span class="pl-8 text-sm">{selectedCoach.born && getRegion(selectedCoach?.born)}</span>
        </p>
        <p>
            年龄
            <span class="pl-8 text-sm">{selectedCoach?.age}</span>
        </p>
        <p>
            年薪
            {#if selectedCoach?.salaryHigh}
                <span class="pl-8 text-sm">
                    {selectedCoach?.salaryHigh} 亿
                </span>
            {/if}
            <span class="pl-{selectedCoach?.salaryHigh ? '2' : '8'} text-sm"
                >{selectedCoach?.salaryLow} 万</span
            >
        </p>
        <p>
            等级
            <span class="pl-8 text-sm">{selectedCoach?.rank && getRank(selectedCoach.rank)}</span>
        </p>
        <p>启用方针</p>
        <div class="pl-4 text-sm text-left">
            {selectedCoach?.activatePlan !== undefined
                ? activatePlan[selectedCoach.activatePlan]
                : ""}
        </div>
        <p>练习方针</p>
        <div class="pl-4 text-sm text-left">
            {selectedCoach?.trainingPlan !== undefined
                ? trainingPlan[selectedCoach.trainingPlan]
                : ""}·{selectedCoach?.trainingStrength !== undefined
                ? trainingStrength[selectedCoach.trainingStrength]
                : ""}
        </div>
        <p>固有风格</p>
        <div class="pl-4 text-sm text-left">
            {#if selectedCoach?.styles && selectedCoach.styles.length > 0}
                {#each selectedCoach.styles as item}
                    {#if item > 0}
                        <div>{getStyle(item)}</div>
                    {/if}
                {/each}
            {/if}
        </div>
        {#if selectedCoach?.spSkill !== undefined && selectedCoach?.spSkill !== null}
            <div class="flex items-center gap-x-2">
                <p>特殊战术</p>
                <Component />
            </div>
            <div class="pl-4 text-sm text-left">
                {getMcoachSkillData()[selectedCoach.spSkill]}
            </div>
        {/if}
        {#if selectedCoach.bringAbroads && selectedCoach.bringAbroads.length > 0}
            <div class="flex items-center gap-x-2">
                <p>留学/集训地</p>
                <Airplane />
            </div>
            <div class="pl-4 text-sm text-left">
                {#each selectedCoach.bringAbroads as abr}
                    <div>{`${getTeamData()[abr.id - 255]}${abr.type === 1 ? " [集训地]" : " [留学地]"}`}</div>
                {/each}
            </div>
        {/if}
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    <RadarChart6 abilities={selectedCoach?.hexagon ?? Array(6).fill(0)} />
    <div
        class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2"
    >
        <p>{selectedCoach?.eval}</p>
    </div>
    <div
        class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2"
    >
        <p>助教特训</p>
        <div class="pl-4 text-sm text-left">
            {#if selectedCoach?.spPrac1 !== undefined}
                <div>{getAcPracData()[selectedCoach.spPrac1]}</div>
            {/if}
            {#if selectedCoach?.spPrac2}
                <div>{getAcPracData()[selectedCoach.spPrac2]}</div>
            {/if}
        </div>
    </div>
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-46 text-sm">{label}</span>
            {#if value}
                {@const tooltipText = `${value[2]}`}
                <Tooltip text={tooltipText} className="w-full">
                    <AbilityBar abilities={value} is100={true} />
                </Tooltip>
            {/if}
        </HStack>
    {/each}
</VStack>
