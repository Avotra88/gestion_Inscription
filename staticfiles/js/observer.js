const observer = new MutationObserver(function(mutationsList, observer) {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            console.log('Un nouveau nœud a été inséré');
        }
    }
});

// Commencer l'observation des ajouts/suppressions de nœuds
observer.observe(document.body, { childList: true, subtree: true });

// Si vous souhaitez arrêter l'observation après 5 secondes (par exemple)
setTimeout(() => {
    observer.disconnect();
    console.log('L\'observation a été arrêtée.');
}, 5000); // L'observation s'arrête après 5 secondes
