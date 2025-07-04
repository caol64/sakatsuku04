<script lang="ts">
    import { setSaveList, setModeState } from "$lib/globalState.svelte";
    import Ps2 from "$lib/icons/Ps2.svelte";

    async function connectPcsx2() {
        if (window.pywebview?.api?.connect_pcsx2) {
            const flag = await window.pywebview.api.connect_pcsx2();
            if (flag) {
                setSaveList([]);
                setModeState("memoryEditor");
            } else {
                alert("请先运行游戏");
            }
        } else {
            alert('API 未加载');
        }
    }
</script>

<div class="flex flex-col items-center justify-center space-y-1 w-full">
    <div class="text-gray-300 text-6xl">
        <Ps2 />
    </div>
    <div class="flex flex-col space-y-2">
        <div class="flex items-center space-x-2 text-sm">
            <button onclick={connectPcsx2} class="text-blue-600 cursor-pointer flex items-center">
                连接 PCSX2 模拟器
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </button>
        </div>
    </div>
</div>
