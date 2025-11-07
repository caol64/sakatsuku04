<script lang="ts">
    import type { TeamPlayer } from "$lib/models";
    import { getPlayerColor, sortedPosition, sortedRegion, getCooperationType, getGrowType, getPosition, getRank, getToneType, fromHex, sortedRank, sortedCooperationType, sortedToneType, sortedStyle, getStyle } from "$lib/utils";
    import VStack from "./Stack/VStack.svelte";
    import teamsData from "$locales/teams_zh.json";
    import DropDown from "$lib/icons/DropDown.svelte";
    import { setIsLoading, getGameYear } from "$lib/globalState.svelte";
    import HStack from "./Stack/HStack.svelte";
    import BPlayerDetails from "./BPlayerDetails.svelte";
    import Close from "$lib/icons/Close.svelte";
    import PlayerIcon from "./PlayerIcon.svelte";

    let keyword = $state("");
    let teamPlayers: TeamPlayer[] = $state([]);

    let showAdvanced = $state(false);

    // 高级筛选字段
    let selectedPos = $state("");
    let selectedCountry = $state("");
    let selectedAge = $state("");
    let selectedRank = $state("");
    let selectedTone = $state("");
    let selectedCooperationType = $state("");
    let selectedStyle = $state("");
    let selectedScoutAction = $state("");
    let placeholderPos = "不指定";
    let placeholderAge = "不指定";
    let placeholderCountry = "不指定";
    let placeholderRank = "不指定";
    let placeholderTone = "不指定";
    let placeholderCooperationType = "不指定";
    let placeholderStyle = "不指定";
    let placeholderScoutAction = "不指定";

    const scoutActions = ["球探搜索", "自由球员", "优先新人", "新人轮选", "青训选拔"];

    let showDrawer = $state(false);
    let playerId = $state(0);
    let age = $state(0);

    function toggleDrawer() {
        showAdvanced = false;
        showDrawer = !showDrawer;
    }

    function showBPlayer(id: number) {
        showAdvanced = false;
        playerId = id;
        age = teamPlayers.filter(i => i.id === id)[0].age;
        showDrawer = true;
    }

    function isSearchValid(name?: string, pos?: number, age?: number, country?: number, rank?: number, cooperation?: number, tone?: number, style?: number, scoutAction?: number): boolean {
        return !!(name || pos || age || country || rank || cooperation || tone || style || scoutAction); // 防止返回undefined
    }


    async function search() {
        const name = keyword || undefined;
        const pos = selectedPos && !isNaN(Number(selectedPos)) ? Number(selectedPos) + 1 : undefined;
        const age = selectedAge && !isNaN(Number(selectedAge)) ? Number(selectedAge) : undefined;
        const country = selectedCountry ? fromHex(selectedCountry) : undefined;
        const rank = selectedRank ? fromHex(selectedRank) + 1 : undefined;
        const cooperation = selectedCooperationType && !isNaN(Number(selectedCooperationType)) ? Number(selectedCooperationType) + 1 : undefined;
        const tone = selectedTone && !isNaN(Number(selectedTone)) ? Number(selectedTone) + 1 : undefined;
        const style = selectedStyle ? fromHex(selectedStyle) : undefined;
        const scoutAction = selectedScoutAction && !isNaN(Number(selectedScoutAction)) ? Number(selectedScoutAction) : undefined;
        if (!isSearchValid(name, pos, age, country, rank, cooperation, tone, style, scoutAction)) {
            alert("请至少填写一个搜索条件（姓名、位置、年龄、国籍、等级、连携、性格、风格、球探活动）");
            return;
        }

        try {
            setIsLoading(true);
            if (window.pywebview?.api?.search_player) {
                teamPlayers = await window.pywebview.api.search_player({
                    name,
                    pos,
                    age,
                    country,
                    rank,
                    cooperation,
                    tone,
                    style,
                    scoutAction
                });
            } else {
                alert('API 未加载');
            }
        } finally {
            setIsLoading(false);
        }
    }

    function toggleAdvance() {
        showDrawer = false;
        showAdvanced = !showAdvanced;
    }

    function getTeamByIndex(index: number) {
        return index !== -1 ? teamsData[index] : "";
    }

    function reset() {
        selectedPos = "";
        selectedCountry = "";
        selectedAge = "";
        selectedRank = "";
        selectedCooperationType = "";
        selectedTone = "";
        selectedScoutAction = "";
    }
</script>

<VStack className="relative p-6 h-full">

    <!-- 顶部搜索栏 -->
    <div class="flex items-center justify-center mb-8">
        <input
            type="text"
            placeholder="输入球员姓名关键字"
            bind:value={keyword}
            onkeydown={(e) => {
                if (e.key === 'Enter') search();
            }}
            class="w-96 px-4 py-1 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
        />
        <button onclick={search} class="w-18 h-8 rounded-md cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 ml-4">
            搜索
        </button>
        <button onclick={toggleAdvance} class="h-8 px-4 rounded-md cursor-pointer text-sm border border-gray-300 dark:border-gray-600 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white ml-2">
            高级
        </button>
    </div>

    <!-- 表格部分 -->
    <div class="overflow-y-auto rounded-lg shadow pb-24">
        <table class="min-w-full text-sm text-left text-gray-900 dark:text-white">
            <thead class="bg-gray-100 dark:bg-gray-800 text-xs uppercase">
                <tr>
                    <th class="px-4 py-3 w-48">球员</th>
                    <th class="px-4 py-3">年龄</th>
                    <th class="px-4 py-3">位置</th>
                    <th class="px-4 py-3">等级</th>
                    <th class="px-4 py-3">风格</th>
                    <th class="px-4 py-3">连携</th>
                    <th class="px-4 py-3">性格</th>
                    <th class="px-4 py-3">身体</th>
                    <th class="px-4 py-3">技术</th>
                    <th class="px-4 py-3">头脑</th>
                    <th class="px-4 py-3 w-48">球队</th>
                </tr>
            </thead>
            <tbody>
                {#each teamPlayers as item}
                    <tr class="border-b border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600">
                        <th scope="row" class="px-2 font-medium text-gray-900 whitespace-nowrap dark:text-white" style={`background-image: linear-gradient(to right, transparent 66%, ${getPlayerColor(item.pos)} 100%)`}>
                            <span class="flex items-center justify-between w-full">
                                <button onclick={() => { showBPlayer(item.id) }} class="cursor-pointer select-text">
                                    {item.name}
                                </button>
                                <PlayerIcon teamPlayer={item} />
                            </span>
                        </th>
                        <td class="px-4 py-2">{item.age}</td>
                        <td class="px-4 py-2">{getPosition(item.pos)}</td>
                        <td class="px-4 py-2">{getRank(item.rank)}</td>
                        <td class="px-4 py-2">{getStyle(item.style)}</td>
                        <td class="px-4 py-2">{getCooperationType(item.cooperationType)}</td>
                        <td class="px-4 py-2">{getToneType(item.toneType)}</td>
                        <td class="px-4 py-2">{getGrowType(item.growTypePhy)}</td>
                        <td class="px-4 py-2">{getGrowType(item.growTypeTec)}</td>
                        <td class="px-4 py-2">{getGrowType(item.growTypeSys)}</td>
                        <td class="px-4 py-2">{getTeamByIndex(item.teamIndex)}</td>
                    </tr>
                {:else}
                    <tr>
                        <td colspan="11" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                            没有匹配的球员
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>

    <!-- 抽屉式高级搜索面板 -->
    <div class="fixed top-0 right-0 h-full w-80 bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 z-50"
        class:translate-x-0={showAdvanced}
        class:translate-x-full={!showAdvanced}>
        <div class="p-6 flex flex-col h-full">
            <h2 class="text-lg font-bold mb-4 text-gray-900 dark:text-white">高级搜索</h2>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">位置</div>
            <div class="input mb-4">
                <select bind:value={selectedPos} class="select">
                    {#if placeholderPos}
                        <option value="" disabled selected>{placeholderPos}</option>
                    {/if}
                    {#each sortedPosition as value, index}
                        <option value={index}>{value}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">年龄</div>
            <div class="input mb-4">
                <select bind:value={selectedAge} class="select">
                    {#if placeholderAge}
                        <option value="" disabled selected>{placeholderAge}</option>
                    {/if}
                    {#each Array.from({length: 40 - 18 + 1}, (_, i) => i + 18) as number}
                        <option value={number}>{number}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">国籍</div>
            <div class="input mb-4">
                <select bind:value={selectedCountry} class="select">
                    {#if placeholderCountry}
                        <option value="" disabled selected>{placeholderCountry}</option>
                    {/if}
                    {#each sortedRegion.slice(50) as [key, value]}
                        <option value={key}>{value}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">等级</div>
            <div class="input mb-4">
                <select bind:value={selectedRank} class="select">
                    {#if placeholderRank}
                        <option value="" disabled selected>{placeholderRank}</option>
                    {/if}
                    {#each sortedRank as [key, value]}
                        <option value={key}>{value}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">连携</div>
            <div class="input mb-4">
                <select bind:value={selectedCooperationType} class="select">
                    {#if placeholderCooperationType}
                        <option value="" disabled selected>{placeholderCooperationType}</option>
                    {/if}
                    {#each sortedCooperationType as [key, value]}
                        <option value={key}>{value}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">性格</div>
            <div class="input mb-4">
                <select bind:value={selectedTone} class="select">
                    {#if placeholderTone}
                        <option value="" disabled selected>{placeholderTone}</option>
                    {/if}
                    {#each sortedToneType as [key, value]}
                        <option value={key}>{value}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">风格</div>
            <div class="input mb-4">
                <select bind:value={selectedStyle} class="select">
                    {#if placeholderStyle}
                        <option value="" disabled selected>{placeholderStyle}</option>
                    {/if}
                    {#each sortedStyle.slice(1, 25) as [key, value]}
                        <option value={key}>{value}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="text-sm font-medium text-gray-700 dark:text-white mb-4">球探活动</div>
            <div class="input mb-4">
                <select bind:value={selectedScoutAction} class="select">
                    {#if placeholderScoutAction}
                        <option value="" disabled selected>{placeholderScoutAction}</option>
                    {/if}
                    {#each scoutActions as item, index}
                        <option value={index + 1}>{item}</option>
                    {/each}
                </select>
                <DropDown />
            </div>

            <div class="mt-4 flex justify-end gap-2">
                <button onclick={() => showAdvanced = false} class="px-4 py-2 cursor-pointer text-sm text-gray-600 dark:text-white hover:underline">
                    关闭
                </button>
                <button onclick={reset} class="py-2 cursor-pointer text-sm text-gray-600 dark:text-white hover:underline">
                    重置
                </button>
            </div>
        </div>
    </div>

    <div class="fixed top-0 left-0 h-full w-full bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 z-50"
        class:translate-x-0={showDrawer}
        class:translate-x-full={!showDrawer}>
        <HStack className="flex-1 h-full overflow-hidden m-2.5">
            <VStack className="w-1/5">
                <button onclick={toggleDrawer} class="cursor-pointer">
                    <Close />
                </button>
            </VStack>
            <BPlayerDetails selectedPlayer={playerId} selectedYear={getGameYear()} age={age} />
        </HStack>
    </div>
</VStack>

<style lang="postcss">
    @reference "tailwindcss";
    .select {
        @apply w-full bg-transparent placeholder:text-slate-400 text-slate-700 dark:text-gray-300 text-sm border border-slate-200 rounded pl-3 pr-8 py-2 transition duration-300 focus:outline-none focus:border-slate-400 hover:border-slate-400 shadow-sm focus:shadow-md appearance-none cursor-pointer;
    }
    .input {
        @apply w-full relative;
    }
</style>
