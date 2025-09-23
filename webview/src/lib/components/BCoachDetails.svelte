<script lang="ts">
    import type { BCoach } from "$lib/models";
    import HStack from "./Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import { getRank, getRegion, getStyle } from "$lib/utils";
    import ability from "$locales/mcoach_abilities_zh.json";
    import AbilityBar from "./AbilityBar.svelte";
    import RadarChart6 from "./RadarChart6.svelte";
    import activatePlan from "$locales/activate_plan_zh.json";
    import trainingPlan from "$locales/training_plan_zh.json";
    import trainingStrength from "$locales/training_strength_zh.json";
    import mcoachSkill from "$locales/mcoach_skill_zh.json";
    import coachType from "$locales/coach_type_zh.json";
    import acPrac from "$locales/ac_prac_zh.json";

    let { selectedCoach = 0 } = $props();

    let bCoach: BCoach = $state({abilities: [], hexagon: []});
    let stats = $state(Array(6).fill(0));

    let abilityPairs = $derived(
        ability.map((label, i) => ({
            label,
            value: [0, 0, bCoach.abilities[i]]
        }))
    );

    async function fetchBCoach() {
        if (window.pywebview?.api?.get_bcoach) {
            bCoach = await window.pywebview.api.get_bcoach(selectedCoach);
            stats = bCoach.hexagon;
        } else {
            alert('API 未加载');
        }
    }

    $effect(() => {
        if(selectedCoach) {
            fetchBCoach();
        }
    });

</script>

<VStack className="w-1/5 mx-1">
    <div class="border border-gray-200 dark:border-gray-600 rounded-md p-4 space-y-2 bg-gray-50 dark:bg-gray-700">
        <p class="flex items-center justify-between select-text">
            姓名
            <span class="flex-1 pl-8 text-sm">{bCoach?.name}</span>
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
            <span class="pl-{bCoach?.salaryHigh ? '2' : '8'} text-sm">{bCoach?.salaryLow} 万</span>
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
            <div><span>野心</span><span class="pl-3">{bCoach?.ambition}</span></div>
            <div><span>毅力</span><span class="pl-3">{bCoach?.persistence}</span></div>
            <div><span>欲望</span><span class="pl-3">{bCoach?.desire}</span></div>
        </div>
        <p>启用方针</p>
        <div class="pl-4 text-sm text-left">
            {bCoach?.activatePlan !== undefined ? activatePlan[bCoach.activatePlan] : ""}
        </div>
        <p>练习方针</p>
        <div class="pl-4 text-sm text-left">
            {bCoach?.trainingPlan !== undefined ? trainingPlan[bCoach.trainingPlan] : ""}·{bCoach?.trainingStrength !== undefined ? trainingStrength[bCoach.trainingStrength] : ""}
        </div>
        {#if bCoach?.spSkill !== undefined && bCoach?.spSkill !== null}
            <p>特殊战术</p>
            <div class="pl-4 text-sm text-left">
                {mcoachSkill[bCoach.spSkill]}
            </div>
        {/if}
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
    </div>
</VStack>
<VStack className="w-3/10 mx-1">
    <RadarChart6 abilities={stats} />
    <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
        <p>{bCoach?.eval}</p>
    </div>
    <div class="border border-gray-200 dark:border-gray-600 rounded-md py-2 px-3 space-y-2 bg-gray-50 dark:bg-gray-700 my-2">
        <p>以助教身份出现时类型</p>
        <div class="pl-4 text-sm text-left">
            {bCoach?.coachTypeCnv !== undefined ? coachType[bCoach.coachTypeCnv] : ""}
        </div>
        <p>助教特训</p>
        <div class="pl-4 text-sm text-left">
            {#if bCoach?.acSpPractice1 !== undefined}
                <div>{acPrac[bCoach.acSpPractice1]}</div>
            {/if}
            {#if bCoach?.acSpPractice2}
                <div>{acPrac[bCoach.acSpPractice2]}</div>
            {/if}
        </div>
    </div>
</VStack>

<VStack className="grow h-full overflow-auto ml-1 pl-1 pb-12">
    {#each abilityPairs as { label, value }}
        <HStack className="items-center">
            <span class="w-24 text-sm">{label}</span>
            {#if value}
                {@const tooltipText = `${value[2]}`}
                <Tooltip text={tooltipText} className="w-full">
                    <AbilityBar abilities={value} is100={true} />
                </Tooltip>
            {/if}
        </HStack>
    {/each}
</VStack>
