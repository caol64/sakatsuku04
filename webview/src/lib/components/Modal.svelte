<script lang="ts">
    import Close from "$lib/icons/Close.svelte";

    let { open, children, close, maxWidth = "max-w-2xl" } = $props();

    function handleBackdropClick(event: MouseEvent) {
        if (event.target === event.currentTarget) {
            close();
        }
    }
</script>

{#if open}
    <div id="default-modal" onclick={handleBackdropClick} tabindex="-1" aria-hidden="true" class="fixed inset-0 z-50 flex justify-center items-center bg-black/50">
        <div class={`relative p-4 w-full ${maxWidth} max-h-full`}>
            <!-- Modal content -->
            <div class="relative bg-white rounded-lg shadow-sm dark:bg-[var(--dark-bg-color)] animate-fade-in">
                <button onclick={close} class="absolute right-4 top-4 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white" aria-label="Close modal">
                    <Close />
                </button>
                {@render children?.()}
            </div>
        </div>
    </div>
{/if}

<style>
    @keyframes fade-in {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    .animate-fade-in {
        animation: fade-in 0.2s ease-out;
    }
</style>
