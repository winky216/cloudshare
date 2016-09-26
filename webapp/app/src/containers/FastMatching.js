'use strict';
import React, { Component } from 'react';

import Header from '../components/common/Header';
import FilterBox from '../components/fastmatching/FilterBox';
import SearchResultBox from '../components/common/searchresult/SearchResultBox';

import './fastmatching.less';

export default class FastMatching extends Component {

  constructor() {
    super();
    this.state = {
      id: '',
      classify: [],
      searchResultDataSource: [],
      pages: 0,
      total: 0,
      spinning: true,
      visible: false,
      postData: {},
    };

    this.loadClassifyData = this.loadClassifyData.bind(this);
    this.handleSearch = this.handleSearch.bind(this);
    this.handleSwitchPage = this.handleSwitchPage.bind(this);
  }

  loadClassifyData() {
    fetch(`/api/classify`, {
      method: 'GET',
    })
    .then(response => response.json())
    .then((json) => {
      if (json.code === 200) {
        this.setState({
          classify: json.data,
        });
      }
    })
  }

  handleSearch(value) {
    const filterData = {};
    for (let key in value) {
      if (key !== 'uses') {
        filterData[key] = value[key];
      }
    }
    const postData = {
      id: '5b8fcdb00d0b11e6bb746c3be51cefca',
      uses: value.uses,
      filterdict: filterData,
    };

    this.setState({
      postData: postData,
      visible: true,
      spinning: true,
    });

    fetch(`/api/mining/lsibyjdid`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Authorization': `Basic ${localStorage.token}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    })
    .then(response => response.json())
    .then((json) => {
      this.setState({
          spinning: false,
          searchResultDataSource: json.data.datas,
          pages: json.data.pages,
          total: json.data.totals,
      });
    })
  }

  handleSwitchPage(page) {
    this.setState({
      spinning: true,
      searchResultDataSource: [],
    });
    fetch(`/api/mining/lsibyjdid`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Authorization': `Basic ${localStorage.token}`,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(Object.assign(this.state.postData, { page: page })),
    })
    .then(response => response.json())
    .then((json) => {
      this.setState({
        spinning: false,
        searchResultDataSource: json.data.datas,
      });
    })
  }

  componentDidMount() {
    const url = window.location.href.split('/');

    this.setState({
      id: url[url.length - 1],
    });
    this.loadClassifyData();
  }

  render() {
    return (
      <div>
        <Header />
        <FilterBox
          classify={this.state.classify}
          visible={this.state.visible}
          total={this.state.total}
          onSearch={this.handleSearch}
        />
        <SearchResultBox
          visible={this.state.visible}
          total={this.state.total}
          spinning={this.state.spinning}
          dataSource={this.state.searchResultDataSource}
          onSwitchPage={this.handleSwitchPage}
        />
      </div>
    );
  }
}