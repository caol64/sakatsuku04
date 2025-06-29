<script lang="ts">
    import { setSaveList, setModeState } from "$lib/globalState.svelte";
    import MemoryCard from "$lib/icons/MemoryCard.svelte";

    async function openFileDialog() {
        const api = window.pywebview?.api;

        if (!api?.pick_file) {
            alert('pywebview API 未加载');
            return;
        }

        try {
            const pageData = await api.pick_file();
            if (!pageData || pageData.length === 0) return;
            setSaveList(pageData);
            setModeState("saveEditor");
        } catch (err) {
            console.error("Error during file open:", err);
            alert("文件读取失败");
        }
    }
</script>

<div class="flex items-center justify-center space-x-20 w-full">
    <div class="text-gray-300 text-6xl">
        <MemoryCard />
    </div>
    <div class="flex flex-col space-y-2">
        <p class="text-gray-700 text-base font-medium">
            请打开存档文件。
        </p>
        <div class="flex items-center space-x-2 text-sm">
            <span>拖放或</span>
            <button onclick={openFileDialog} class="text-blue-600 cursor-pointer flex items-center">
                从计算机中选择
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </button>
        </div>
    </div>
</div>


<style lang="postcss">
    @reference "tailwindcss";
</style>
