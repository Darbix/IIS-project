const DEF_SPACE_X = 10 // px Horizontal initial gap
const DEF_SPACE_Y = 50 // px Vertical initial gap

function create_diagram(){
    var diagram = document.getElementById("diagram");
    var divs = diagram.getElementsByClassName("cell");

    if(divs && divs.length > 0){
        var W = divs[0].offsetWidth;  // Width of the div cell
        var H = divs[0].offsetHeight; // Height of the div cell

        var SPX = DEF_SPACE_X; // Horizontal space between cells, that increases each row
        var SPY = DEF_SPACE_Y; // Vertical Space between cells
        
        var x = DEF_SPACE_X; // Current X position of the cell
        var y = DEF_SPACE_X; // Current Y position of the cell

        var INITX = DEF_SPACE_X // X gap between the left row side and the first row cell
        var endTeamRow = false; // Detect thah all the teams are loaded

        var nPrev = 0; // Number of cells in a previous row
        var nCurr = 0; // Current number of cells counter

        // SVG plane behind the cells
        var svg = document.createElementNS("http://www.w3.org/2000/svg","svg");

        for(var i=0; i<divs.length; i++){
            var d = divs[i];
            
            // If a team row is done, prepare for the new line
            if(!endTeamRow && !d.classList.contains("cell-team"))
                endTeamRow = true;

            // If a number of cells is >= half of the previous count, create a new row
            if(nCurr >= nPrev / 2 && endTeamRow){
                // Only once (after a team row) compute the size of an SVG plane 
                if(nPrev == 0){
                    svg.setAttribute("width", nCurr * (W + SPX) + SPX);
                    svg.setAttribute("height", (1 + Math.ceil(Math.log2(nCurr))) * (H + SPY) + SPX);
                }
                
                // Increase the left gap 
                INITX += (W + SPX) / 2;
                // Increse the horizontal space between cells 
                SPX = 2 * SPX + W;

                // Init new first cell position
                y += H + SPY;
                x = INITX;

                nPrev = nCurr;
                nCurr = 0;
            }
            nCurr++;
            
            // If not on the first row, draw connecting lines
            if(endTeamRow){
                svg.append(getLine((x - (W + SPX) / 4 + W / 2), (y - H / 2 - SPY), (x + W / 2), (y + H / 2)));
                svg.append(getLine((x + (W + SPX) / 4 + W / 2), (y - H / 2 - SPY), (x + W / 2), (y + H / 2)));
            }

            d.style.left = x + "px";
            d.style.top = y + "px";

            x += W + SPX;
        }

        // Append the SVG with lines to a diagram
        diagram.append(svg);
        // Change initial style colors of the elements 
        change_all_styles();
    }
}

function getLine(x1, y1, x2, y2){
    /**
     * Create a line element between 2 points using coordinates
     * @return SVG line
     */

    var line = document.createElementNS("http://www.w3.org/2000/svg","line");

    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("stroke", "white")
    line.setAttribute("stroke-width", "3")

    return line;
}

function change_all_styles(){
    /**
     * Go through all the cells, get proper IDs and apply change_winner_style() function on each
     */

    var matches = diagram.getElementsByClassName("cell-match");

    if(matches){
        for(var i=0; i<matches.length; i++){
            m = matches[i];

            t1 = m.getElementsByClassName("cell-match-t1")[0];
            t2 = m.getElementsByClassName("cell-match-t2")[0];

            sc1 = m.getElementsByClassName("cell-match-s1")[0];
            sc2 = m.getElementsByClassName("cell-match-s2")[0]

            // Cell could be blank, when the previous matches have no winners yet
            if(t1 !== undefined && t2 !== undefined && sc1 !== undefined && sc2 !== undefined)
                change_winner_style(sc1.id, sc2.id, t1.id, t2.id);
        }
    }
}

function change_winner_style(iA_id, iB_id, tA_id, tB_id){
    /**
     * Change a name text and input background color of a winner team
     * @param {string} iA_id Match team A input ID for a score A
     * @param {string} iB_id Match team B input ID for a score B 
     * @param {string} tA_id Match team A div ID for a name A
     * @param {string} tB_id Match team B div ID for a name B
     */

    var teamA = document.getElementById(tA_id);
    var teamB = document.getElementById(tB_id);

    var inputA = document.getElementById(iA_id)
    var inputB = document.getElementById(iB_id)

    var scoreA = inputA.value;
    var scoreB = inputB.value;

    // Default CSS colors
    teamA.style.color = inputA.style.background = inputA.style.color = "";
    teamB.style.color = inputB.style.background = inputB.style.color = "";

    // Color the winner's attributes
    if(scoreA > scoreB)
        teamA.style.color = inputA.style.background = "yellow";
    else if(scoreA < scoreB)
        teamB.style.color = inputB.style.background = "yellow";
    // Scores cannot be the same
    else
        inputA.style.color = inputB.style.color = "red";
}