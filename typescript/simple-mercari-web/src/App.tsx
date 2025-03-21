import { useState } from 'react';
import './App.css';
import { ItemList } from '~/components/ItemList';
import { Listing } from '~/components/Listing';

function App() {
  // reload ItemList after Listing complete
  const [reload, setReload] = useState(true);
  return (
    <div className='divider'>
      <header className="Title">
        <p>
          <b>Simple Mercari</b>
        </p>
      </header>
      <hr className="divider"/>
      {/* <div className="MainContainer"> */}
        <div>
          <Listing onListingCompleted={() => setReload(true)} />
        </div>
        <div>
          <ItemList reload={reload} onLoadCompleted={() => setReload(false)} />
        </div>
      {/* </div> */}
    </div>
  );
}

export default App;
