import React, { useState } from 'react';

import preval from 'preval.macro'


import './scss/app.scss';
import Cards from './components/Cards.js';
import data from './fixtures/data.json';
import './scss/search_input.scss';
import search from './images/search.svg'



function App() {
  const [searchText, setSearchText] = useState("");

  const filteredItems = data.filter(
    ({ name, teachers, c }) =>
      name.toLowerCase().includes(searchText.toLowerCase()) ||
      c.toLowerCase().includes(searchText.toLowerCase()) ||
      teachers.filter(t => t.toLowerCase().includes(searchText.toLowerCase())).length > 0
  );

  const lastUpdate = preval`module.exports = new Date().toLocaleString();`;

  return (
    <div className="App">
      <div className="container">
        <div className="title">
          <h1>
            Programmi Svolti a.s. 2025/26
          </h1>
        </div>
        <div className="description">
          <p>
            In questa pagina potrai trovare i programmi svolti per tutte le materie relative all'anno scolastico 2025/26.
          </p>
          <h2>
            Utilizza il campo di testo per cercare il programma che ti interessa
          </h2>
          <p>Puoi cercare per:</p>
          <ul>
            <li><strong>Cognome</strong> del docente</li>
            <li><strong>Nome</strong> della materia</li>
            <li><strong>Denominazione</strong> della classe (es. <i>3ITETB</i>, <i>2G</i>, <i>4ITIAB</i>)</li>
          </ul>
          <p>
            <u>N.B. La pagina &egrave; in continuo aggiornamento.</u>
            <br />
            Ultimo aggiornamento: <strong>{lastUpdate}</strong>
          </p>
        </div>
        <div className="SearchInput">
          <div className="inputWrapper">
            <img src={search} alt="Search" />
            <div className="inputField">
              <input
                type="text"
                placeholder="Inserisci classe, materia o nome del docente"
                value={searchText}
                onChange={({ target }) => setSearchText(target.value)}
              />
              <div className="line"></div>
            </div>
          </div>
        </div>
      </div>
      <div className="container">
        <Cards className="cards"
          items={filteredItems}
        />
      </div>
    </div>
  );
}

export default App;
