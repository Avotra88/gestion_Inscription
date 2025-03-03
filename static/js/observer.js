const observer = new MutationObserver(function(mutationsList, observer) {
    for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(node => {
                console.log('Nouveau nœud ajouté:', node);
            });
        }
    }
});

// Commencer l'observation des ajouts/suppressions de nœuds
observer.observe(document.body, { childList: true, subtree: true });

// Si tu souhaites arrêter l'observation après 5 secondes
setTimeout(() => {
    observer.disconnect();
    console.log('L\'observation a été arrêtée.');
}, 5000);
