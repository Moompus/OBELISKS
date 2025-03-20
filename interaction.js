window.onload = function() {
    const correctBlueDivs = [0, 4, 6]; // correct indices for blue divs
    const hiddenTruthElements = document.querySelectorAll('.hidden-truth');

    // select all divs inside container
    const divs = document.querySelectorAll('.container div');

    // add event listener to each div
    divs.forEach((div) => {
        div.addEventListener("click", function() {
            if (div.style.backgroundColor === 'blue') {
                div.style.backgroundColor = '';
            } else {
                div.style.backgroundColor = 'blue';
            }
            
            // Count blue divs
            const blueDivs = Array.from(divs).filter(d => d.style.backgroundColor === 'blue');
            
            // Check if the correct pattern is selected
            if (blueDivs.length === 3) {
                const blueIndices = blueDivs.map(d => Array.from(divs).indexOf(d));
                const isCorrect = 
                    correctBlueDivs.length === blueIndices.length && 
                    correctBlueDivs.every(index => blueIndices.includes(index));
                
                if (isCorrect) {
                    // Success: make all divs green
                    divs.forEach(d => {
                        d.style.backgroundColor = 'limegreen';
                    });
                    
                    // Reveal the hidden truth
                    hiddenTruthElements.forEach(element => {
                        element.classList.add('truth');
                    });
                } else {
                    // Failure: make all divs red and reset after 1 second
                    divs.forEach(d => {
                        d.style.backgroundColor = 'red';
                    });
                    
                    // Hide the truth if it was previously shown
                    hiddenTruthElements.forEach(element => {
                        element.classList.remove('truth');
                    });
                    
                    setTimeout(() => {
                        divs.forEach(d => {
                            d.style.backgroundColor = '';
                        });
                    }, 1000);
                }
            }
        });
    });
};


// je dingen klikken
// je dingen opslaan in arrays
// je kan variabelen
// je kan dingen tellen
// je html ophalen en kijken wat erin zit
// je kan de css uitlezen van een element
// je kan de css veranderen van een element
// je kan een event listener toevoegen aan een element



// queesste
// 1. probeer als je klik de background blauw te maken
// probeer te achterhalen hoeveel divs er blauw
// als er meer dan 3 blauw zijn, controleer of de juist 3 blauw zijn
// is dat niet zo, geef een melding door een div te tonen die hiervoor onzichtbaar was
// is dat wel zo, geef melding die laat weten, groot succes
// reset alle blauwe divs naar groen
// reset alles naar wit
// innerhtml

