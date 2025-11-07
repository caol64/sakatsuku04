<script lang="ts">
    import { setSaveList, setModeState } from "$lib/globalState.svelte";
    import Forward from "$lib/icons/Forward.svelte";
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
                <Forward />
            </button>
            <a href="https://yuzhi.tech/docs/saka04/pcsx2" target="_blank" class="text-blue-600 cursor-pointer flex items-center">
                遇到问题？
                <Forward />
            </a>
        </div>
    </div>
</div>
