<script>
    let board = Array(3).fill("").map(() => Array(3).fill(""));

    function handleClick(row, col) {
        console.log(`Clicked on row ${row} and col ${col}`);
    }
</script>

<style>
    .board {
        display: grid;
        grid-template-columns: repeat(3, 0fr);
        gap: 10px;
    }
    button {
        height: 150px;
        width: 150px;
    }
</style>

<div class="board">
    {#each board as row, i}
        {#each row as cell, j}
            <button on:click={() => handleClick(i, j)}>{cell}</button>
        {/each}
    {/each}
</div>