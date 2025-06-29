<script lang="ts">
    import { getBaseData } from "$lib/globalState.svelte";
    import HStack from "$lib/components/Stack/HStack.svelte";
    import VStack from "./Stack/VStack.svelte";
    import { onMount } from "svelte";
    import { defaultBaseData } from "$lib/models";

    const pattern = "^([1-9][0-9]{0,3}|0)$";
    let baseData = $state(defaultBaseData);

    $effect(() => {
        baseData = getBaseData();
    });
</script>

<VStack>
    <div class="mb-6 mt-3">
        <label for="clubname">Club Name</label>
        <input id="clubname" bind:value={ baseData.clubName } class="input" required />
    </div>
    <div class="mb-6">
        <label for="fundHeigh">Club Fund</label>
        <HStack className="gap-4">
            <div class="relative">
                <input type="text" id="fundHeigh" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ baseData.fundHeigh } class="input" required />
                <div class="inner">
                    <span>亿</span>
                </div>
            </div>
            <div class="relative">
                <input type="text" id="fundLow" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ baseData.fundLow } class="input" required />
                <div class="inner">
                    <span>万</span>
                </div>
            </div>
        </HStack>
    </div>
    <div class="mb-6">
        <label for="year">Game Year</label>
        <HStack className="gap-4">
            <div class="relative">
                <input type="text" id="year" maxlength="4" pattern={pattern} title="请输入 0 到 9999 之间的整数" bind:value={ baseData.year } class="input" required />
                <div class="inner">
                    <span>年</span>
                </div>
            </div>
            <div class="relative">
                <input type="text" id="month" maxlength="2" pattern={pattern} title="请输入 1 到 12 之间的整数" bind:value={ baseData.month } class="input" required />
                <div class="inner">
                    <span>月</span>
                </div>
            </div>
            <div class="relative">
                <input type="text" id="date" maxlength="2" pattern={pattern} title="请输入 1 到 31 之间的整数" bind:value={ baseData.date } class="input" required />
                <div class="inner">
                    <span>日</span>
                </div>
            </div>
        </HStack>
    </div>
    <div class="mb-6">
        <label for="managerName">Manager Name</label>
        <input id="managerName" bind:value={ baseData.managerName } class="input" required />
    </div>
    <div class="mb-6">
        <label for="gameDifficulty">Game Difficulty</label>
        <span class="text-sm">{ baseData.difficulty }</span>
        <input id="gameDifficulty" type="range" bind:value={ baseData.difficulty } class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700">
    </div>
</VStack>

<style lang="postcss">
    @reference "tailwindcss";
    label {
        @apply block mb-2 text-sm font-medium text-gray-900 dark:text-white;
    }
    .input {
        @apply bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500;
    }
    .inner {
        @apply absolute inset-y-0 end-0 top-0 flex items-center pe-3.5 pointer-events-none;
    }
</style>
