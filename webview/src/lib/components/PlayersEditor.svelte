<script lang="ts">
    import VStack from "./Stack/VStack.svelte";
    import DropDown from "$lib/icons/DropDown.svelte";
    import type { MyPlayer, MyPlayerAbility } from "$lib/models";
    import { fromHex, sortedAbilities, sortedCooperationType, sortedGrowType, sortedPosition, sortedRegion, sortedStyle, sortedToneType, toHex } from "$lib/utils";
    import HStack from "./Stack/HStack.svelte";
    import Tooltip from "./Tooltip.svelte";
    import comp from "$locales/comp_zh.json";

    type Props = { player: MyPlayer, team: number, onSave: () => void; };

    let { player, team, onSave }: Props = $props();
    let selectedBorn = $state(toHex(player.born));
    let selectedPos = $state(toHex(player.pos));
    let selectedStyle = $state(toHex(player.style));
    let selectedCooperationType = $state(toHex(player.cooperationType));
    let selectedToneType = $state(toHex(player.toneType));
    let selectedGrowTypePhy = $state(toHex(player.growTypePhy));
    let selectedGrowTypeTec = $state(toHex(player.growTypeTec));
    let selectedGrowTypeSys = $state(toHex(player.growTypeSys));
    let selectedAbilityIndex = $state(0);
    let selectedAge = $state(player.age);
    let selectedSalaryHigh = $state(player.salaryHigh);
    let selectedSalaryLow = $state(player.salaryLow);
    let selectedAbroadTimes = $state(player.abroadTimes);
    let playAbilities = player.abilities.map(ability => ({ ...ability }));
    let selectedAbility: MyPlayerAbility = $state(playAbilities[0]);
    let selectedOfferYearsPassed = $state(player.offerYearsPassed);
    let selectedOfferYearsTotal = $state(player.offerYearsTotal);

    function selectAbility() {
        selectedAbility = playAbilities[selectedAbilityIndex];
    }

    function toCurrentMax() {
        for (let i = 0; i < player.abilities.length; i++) {
            playAbilities[i].current = player.abilities[i].currentMax;
            playAbilities[i].currentMax = player.abilities[i].currentMax;
        }
        selectedAbility = playAbilities[selectedAbilityIndex];
    }

    function toMax() {
        for (let i = 0; i < player.abilities.length; i++) {
            playAbilities[i].current = player.abilities[i].max;
            playAbilities[i].currentMax = player.abilities[i].max;
        }
        selectedAbility = playAbilities[selectedAbilityIndex];
    }

    function checkAbility(): boolean {
        playAbilities[selectedAbilityIndex] = selectedAbility;
        for (let i = 0; i < playAbilities.length; i++) {
            if (playAbilities[i].current > 65535
                || playAbilities[i].currentMax > 65535
                || playAbilities[i].max > 65535) {
                    alert(`能力值不能超过65535\n${playAbilities[i].current}  ${playAbilities[i].currentMax}  ${playAbilities[i].max}`);
                    return false;
                }
            if (playAbilities[i].current > playAbilities[i].currentMax
                || playAbilities[i].currentMax > playAbilities[i].max
                || playAbilities[i].current > playAbilities[i].max) {
                    alert(`能力值不能超过其上限\n${playAbilities[i].current}  ${playAbilities[i].currentMax}  ${playAbilities[i].max}`);
                    return false;
                }

        }
        return true;
    }

    function checkMoney(): boolean {
        if (selectedSalaryHigh === undefined || selectedSalaryLow === undefined || isNaN(selectedSalaryHigh) || isNaN(selectedSalaryLow)) {
            alert("金额不正确");
            return false;
        }

        const high = Number(selectedSalaryHigh);
        const low = Number(selectedSalaryLow);

        if (!Number.isInteger(high) || !Number.isInteger(low) || high < 0 || low < 0) {
            alert("金额必须为正整数");
            return false;
        }
        if ((high * 10000 + low <= 100)) {
            alert("年薪不能低于100万");
            return false;
        }
        return true;
    }

    async function submitSave() {
        if (checkAbility() && checkMoney()) {
            const newPlayer: MyPlayer = { ...player };
            newPlayer.abilities = playAbilities;
            newPlayer.age = selectedAge;
            newPlayer.abroadTimes = selectedAbroadTimes;
            newPlayer.salaryHigh = selectedSalaryHigh;
            newPlayer.salaryLow = selectedSalaryLow;
            newPlayer.offerYearsPassed = selectedOfferYearsPassed;
            newPlayer.offerYearsTotal = selectedOfferYearsTotal;
            newPlayer.born = fromHex(selectedBorn);
            newPlayer.pos = fromHex(selectedPos);
            newPlayer.style = fromHex(selectedStyle);
            newPlayer.cooperationType = fromHex(selectedCooperationType);
            newPlayer.toneType = fromHex(selectedToneType);
            newPlayer.growTypePhy = fromHex(selectedGrowTypePhy);
            newPlayer.growTypeTec = fromHex(selectedGrowTypeTec);
            newPlayer.growTypeSys = fromHex(selectedGrowTypeSys);
            if (window.pywebview?.api?.save_my_player) {
                const { message } = await window.pywebview.api.save_my_player(newPlayer, team);
                if (message === "success") {
                    alert("修改成功");
                    onSave();
                } else {
                    alert(message);
                }
            } else {
                alert('API 未加载');
            }
        }
    }

    function clearComp() {
        if (player.comp) {
            for (let i = 0; i < player.comp.length; i++) {
                player.comp[i] = 0;
            }
        }
    }
</script>

<VStack>
    <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-600 rounded-t bg-gray-50 dark:bg-gray-800">
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white tracking-wide">
            球员修改 - {player.name}
        </h3>
    </div>
    <div class="form">
        <div class="label">年龄</div>
        <HStack className="input items-center">
            <input id="age" type="range" min="16" max="40" bind:value={ selectedAge } class="range">
            <span class="text-sm ml-2">{ selectedAge }</span>
        </HStack>
    </div>
    <div class="form">
        <div class="label">留学次数</div>
        <HStack className="input items-center">
            <input id="abroadTimes" type="range" min="0" max="9" bind:value={ selectedAbroadTimes } class="range">
            <span class="text-sm ml-2">{ selectedAbroadTimes }</span>
        </HStack>
    </div>
    <div class="form">
        <div class="label">出生地</div>
        <div class="input">
            <select bind:value={selectedBorn} class="select">
                {#each sortedRegion as [key, value]}
                    <option value={key}>{value}</option>
                {/each}
            </select>
            <DropDown />
        </div>
    </div>
    <div class="form">
        <div class="label">位置</div>
        <div class="input">
            <select bind:value={selectedPos} class="select">
                {#each sortedPosition as [key, value]}
                    <option value={key}>{value}</option>
                {/each}
            </select>
            <DropDown />
        </div>
    </div>
    <div class="form">
        <div class="label">年薪</div>
        <div class="input">
            <HStack className="gap-4">
                <div class="relative">
                    <input type="text" maxlength="4" title="请输入 0 到 9999 之间的整数" bind:value={ selectedSalaryHigh } class="money-input" required />
                    <div class="inner">
                        <span>亿</span>
                    </div>
                </div>
                <div class="relative">
                    <input type="text" maxlength="4" title="请输入 0 到 9999 之间的整数" bind:value={ selectedSalaryLow } class="money-input" required />
                    <div class="inner">
                        <span>万</span>
                    </div>
                </div>
            </HStack>
        </div>
    </div>
    <div class="form">
        <div class="label">合同</div>
        <div class="input">
            <HStack className="gap-x-4 grid grid-cols-[6fr_1fr_6fr] text-left">
                <HStack className="input items-center">
                    <input id="offerYearsPassed" type="range" min="0" max="5" bind:value={ selectedOfferYearsPassed } class="thin-range">
                    <span class="text-sm ml-2">{ selectedOfferYearsPassed }</span>
                </HStack>
                <div>/</div>
                <HStack className="input items-center">
                    <input id="offerYearsTotal" type="range" min="1" max="5" bind:value={ selectedOfferYearsTotal } class="thin-range">
                    <span class="text-sm ml-2">{ selectedOfferYearsTotal }</span>
                </HStack>
            </HStack>
        </div>
    </div>
    <div class="form">
        <div class="label">风格</div>
        <div class="input">
            <select bind:value={selectedStyle} class="select">
                {#each sortedStyle as [key, value]}
                    <option value={key}>{value}</option>
                {/each}
            </select>
            <DropDown />
        </div>
    </div>
    <div class="form">
        <div class="label">连携</div>
        <div class="input">
            <select bind:value={selectedCooperationType} class="select">
                {#each sortedCooperationType as [key, value]}
                    <option value={key}>{value}</option>
                {/each}
            </select>
            <DropDown />
        </div>
    </div>
    <div class="form">
        <div class="label">性格</div>
        <div class="input">
            <select bind:value={selectedToneType} class="select">
                {#each sortedToneType as [key, value]}
                    <option value={key}>{value}</option>
                {/each}
            </select>
            <DropDown />
        </div>
    </div>
    <div class="form">
        <div class="label">成长类型</div>
        <HStack className="items-center space-x-2">
            <Tooltip text="身体" width="60px">
                <div class="input">
                    <select bind:value={selectedGrowTypePhy} class="thin-select">
                        {#each sortedGrowType as [key, value]}
                            <option value={key}>{value}</option>
                        {/each}
                    </select>
                    <DropDown />
                </div>
            </Tooltip>
            <Tooltip text="技术" width="60px">
                <div class="input">
                    <select bind:value={selectedGrowTypeTec} class="thin-select">
                        {#each sortedGrowType as [key, value]}
                            <option value={key}>{value}</option>
                        {/each}
                    </select>
                    <DropDown />
                </div>
            </Tooltip>
            <Tooltip text="头脑" width="60px">
                <div class="input">
                    <select bind:value={selectedGrowTypeSys} class="thin-select">
                        {#each sortedGrowType as [key, value]}
                            <option value={key}>{value}</option>
                        {/each}
                    </select>
                    <DropDown />
                </div>
            </Tooltip>
        </HStack>
    </div>
    <div class="form">
        <div class="label">能力</div>
        <div class="input">
            <select bind:value={selectedAbilityIndex} onchange={selectAbility} class="select">
                {#each sortedAbilities as value, index}
                    <option value={index}>{value}</option>
                {/each}
            </select>
            <DropDown />
        </div>
    </div>
    <div class="form">
        <div class="label">能力值</div>
        <HStack className="items-center space-x-2">
            <Tooltip text="当前" width="60px">
                <div class="input">
                    <input type="number" min="1" max="65535" bind:value={selectedAbility.current} class="number" required />
                </div>
            </Tooltip>
            <Tooltip text="潜力" width="60px">
                <div class="input">
                    <input type="number" min="1" max="65535" bind:value={selectedAbility.currentMax} class="number" required />
                </div>
            </Tooltip>
            <Tooltip text="上限" width="60px">
                <div class="input">
                    <input type="number" min="1" max="65535" bind:value={selectedAbility.max} class="number" required />
                </div>
            </Tooltip>
        </HStack>
    </div>
    <div class="form">
        <div class="label">不满</div>
        <HStack className="items-center space-x-2">
            {#if player.comp && player.comp.length > 0}
                {#each player.comp as item, i}
                    <Tooltip text={comp[i]} width="80px">
                        <span class="text-sm">{item}</span>
                    </Tooltip>
                {/each}
            {/if}
        </HStack>
    </div>

    <div class="mt-1 flex items-center justify-end p-4 border-t border-gray-200 rounded-b dark:border-gray-600">
        <button onclick={clearComp} class="ms-3 py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 cursor-pointer">消除不满</button>
        <button onclick={toCurrentMax} class="ms-3 py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 cursor-pointer">所有能力到达当前上限</button>
        <button onclick={toMax} class="ms-3 py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 cursor-pointer">所有能力到达最高上限</button>
        <button onclick={submitSave} class="ms-3 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 cursor-pointer">保存</button>
    </div>
</VStack>

<style lang="postcss">
    @reference "tailwindcss";
    .select {
        @apply w-40 bg-transparent placeholder:text-slate-400 text-slate-700 dark:text-gray-300 text-sm border border-slate-200 rounded pl-3 pr-8 py-2 transition duration-300 focus:outline-none focus:border-slate-400 hover:border-slate-400 shadow-sm focus:shadow-md appearance-none cursor-pointer;
    }
    .money-input {
        @apply w-30 bg-transparent placeholder:text-slate-400 text-slate-700 dark:text-gray-300 text-sm border border-slate-200 rounded pl-3 pr-8 py-2 transition duration-300 focus:outline-none focus:border-slate-400 hover:border-slate-400 shadow-sm focus:shadow-md;
    }
    .thin-select {
        @apply w-22 bg-transparent placeholder:text-slate-400 text-slate-700 dark:text-gray-300 text-sm border border-slate-200 rounded pl-3 pr-8 py-2 transition duration-300 focus:outline-none focus:border-slate-400 hover:border-slate-400 shadow-sm focus:shadow-md appearance-none cursor-pointer;
    }
    .form {
        @apply grid grid-cols-[1fr_2fr] my-2 items-center;
    }
    .range {
        @apply w-52 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700;
    }
    .thin-range {
        @apply w-18 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700;
    }
    .label {
        @apply justify-self-end w-fit px-4;
    }
    .input {
        @apply w-fit relative;
    }
    .number {
        @apply w-28 bg-white border border-gray-300 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 shadow-sm focus:shadow-md;
    }
    .inner {
        @apply absolute inset-y-0 end-0 top-0 flex items-center pe-3.5 pointer-events-none;
    }
</style>
