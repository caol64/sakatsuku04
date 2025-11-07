<script lang="ts">
    import Forward from "$lib/icons/Forward.svelte";
    import { type Coach } from "$lib/models";
    import { getRank, getTeamData } from "$lib/utils";
    import acPrac from "$locales/ac_prac_zh.json";
    import mcoachSkill from "$locales/mcoach_skill_zh.json";

    let { selectedCoach, showDrawer = $bindable() }: {selectedCoach: Coach, showDrawer: boolean} = $props();

    function showBCoach() {
        showDrawer = true;
    }
</script>

<div class="h-fit bg-gray-50 dark:bg-gray-700 rounded-2xl shadow p-6 flex flex-col space-y-4 text-sm">
    {#if selectedCoach.id && selectedCoach.id >= 20000}
        <div class="flex justify-center">
            <button onclick={showBCoach} class="cursor-pointer flex items-center">
                查看数据库
                <Forward />
            </button>
        </div>
    {/if}
    {#if selectedCoach.age !== undefined && selectedCoach.age > 0}
        <p class="font-medium">
            年龄
            <span class="pl-8 text-sm">
                {selectedCoach.age}
            </span>
        </p>
    {/if}
    {#if selectedCoach.offerYears !== undefined && selectedCoach.offerYears > 0}
        <p class="font-medium">
            合约
            <span class="pl-8 text-sm">
                {selectedCoach.contractYears ?? 0} / {selectedCoach.offerYears} 年
            </span>
        </p>
    {/if}
    {#if selectedCoach.salaryHigh || selectedCoach.salaryLow}
        <p class="font-medium">
            年薪
            {#if selectedCoach.salaryHigh}
                <span class="pl-8 text-sm">
                    {selectedCoach.salaryHigh} 亿
                </span>
            {/if}
            <span class="pl-{selectedCoach.salaryHigh ? '2' : '8'} text-sm">{selectedCoach.salaryLow} 万</span>
        </p>
    {/if}
    {#if selectedCoach.rank !== undefined && selectedCoach.rank >= 0}
        <p class="font-medium">
            等级
            <span class="pl-8 text-sm">
                {getRank(selectedCoach.rank)}
            </span>
        </p>
    {/if}
    {#if selectedCoach.spPrac1 !== null || selectedCoach.spPrac2 !== null}
        <p class="font-medium">助教特训</p>
        {#if selectedCoach.spPrac1 !== undefined}
            <p class="pl-8 text-sm font-medium">
                {acPrac[selectedCoach.spPrac1]}
            </p>
        {/if}
        {#if selectedCoach.spPrac2 !== undefined}
            <p class="pl-8 text-sm font-medium">
                {acPrac[selectedCoach.spPrac2]}
            </p>
        {/if}
    {/if}
    {#if selectedCoach.spSkill !== undefined && selectedCoach.spSkill !== null}
        <p class="font-medium">
            特殊战术
            <span class="pl-8 text-sm">
                {mcoachSkill[selectedCoach.spSkill]}
            </span>
        </p>
    {/if}
    {#if selectedCoach.bringAbroads && selectedCoach.bringAbroads.length > 0}
        <p class="font-medium">留学/集训地</p>
        {#each selectedCoach.bringAbroads as abr}
            <p class="font-medium pl-8">
                {`${getTeamData()[abr.id - 255]}${abr.type === 1 ? " [集训地]" : " [留学地]"}${abr.isEnabled ? "  (已获得)" : ""}`}
            </p>
        {/each}
    {/if}
</div>
