'use strict';
import React, { Component, PropTypes } from 'react';

import LayoutHeader from '../../common/LayoutHeader';
import LayoutContainer from '../../common/LayoutContainer';
import SubheadNav from 'components/subhead-nav';
import {
  CardContainer,
  CardContent
} from 'components/card-container';

import { getCurrentActive } from 'utils/sider-menu-list';

import websiteText from 'config/website-text';

const language = websiteText.zhCN;

class Layout extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedKey: getCurrentActive(props)
    };
    this.handleSubheadNavClick = this.handleSubheadNavClick.bind(this);
    this.getTitle = this.getTitle.bind(this);
  }

  handleSubheadNavClick(e) {
    this.setState({
      selectedKey: e.key
    });
  }

  getTitle(key, menus) {
    let title = '';

    for (let i = menus.length - 1; i >= 0; i--) {
      if (menus[i].key === key) {
        title = menus[i].title;
      }
    }

    return title;
  }

  render() {
    const menus = [{
      key: 'jobdescription',
      title: language.OPEN_JOB_DESCRIPTION,
      url: '/jobdescription'
    }, {
      key: 'customer',
      title: language.OWN_CUSTOMER_MANAGEMENT,
      url: '/customer'
    }, {
      key: 'company',
      title: language.DEVELOPMENT_CUSTOMER_MANAGEMENT,
      url: '/company/list'
    }];

    const cardContentTitle = this.getTitle(this.state.selectedKey, menus);

    return (
      <div>
        <LayoutHeader />
        <SubheadNav
          menus={menus}
          selectedKeys={[this.state.selectedKey]}
          style={{ marginLeft: 338 }}
          onClick={this.handleSubheadNavClick}
        />
        <LayoutContainer>
          <CardContainer>
            <CardContent title={cardContentTitle}>
              {this.props.children}
            </CardContent>
          </CardContainer>
        </LayoutContainer>
      </div>
    );
  }
}

Layout.propTypes = {
  children: PropTypes.element
};

export default Layout;
