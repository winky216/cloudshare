import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';

import enUS from 'antd/lib/locale-provider/en_US';
import { LocaleProvider } from 'antd';

import UserInfo from '../containers/UserInfo';
import BrowsingHistory from '../components/userinfo/BrowsingHistory';
import Bookmark from '../components/userinfo/Bookmark';

ReactDOM.render(
  <LocaleProvider locale={enUS}>
    <Router history={hashHistory}>
      <Route path="/" component={UserInfo}>
        <IndexRoute component={BrowsingHistory}/>
        <Route path="/browsingHistory" component={BrowsingHistory} />
        <Route path="/bookmark" component={Bookmark} />
      </Route>
    </Router>
  </LocaleProvider>,
  document.getElementById('app')
);