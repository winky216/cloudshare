'use strict';
import React, { Component, PropTypes } from 'react';

import CompanyInfo from './CompanyInfo';
import CreateNewCompany from './CreateNewCompany';
import EnhancedInput from '../../../components/enhanced-input';
import ButtonWithModal from '../../../components/button-with-modal';

import {
  message,
  Pagination,
  Spin,
  Upload,
  Button,
  Icon
} from 'antd';

import {
  getCustomerList,
  getAllCompany,
  getAllCompanyBySearch,
  updateCompanyInfo,
  updateCustomer,
  createCompany,
} from '../../../request/company';

import websiteText from '../../../config/website-text';

const language = websiteText.zhCN;

class CompanyList extends Component {
  constructor() {
    super();
    this.state = {
      current: 1,
      pageSize: 40,
      total: 0,
      searchWord: '',
      dataSource: [],
      customerIDList: [],
      loading: false,
      visible: false,
    };
    this.handleSave = this.handleSave.bind(this);
    this.handleRemove = this.handleRemove.bind(this);
    this.handleSeachClick = this.handleSeachClick.bind(this);
    this.handleShowSizeChange = this.handleShowSizeChange.bind(this);
    this.handlePaginationChange = this.handlePaginationChange.bind(this);
    this.handleCreateCompanySubmit = this.handleCreateCompanySubmit.bind(this);
    this.handleUploadBtnClick = this.handleUploadBtnClick.bind(this);
    this.handleUploadModalCancel = this.handleUploadModalCancel.bind(this);
    this.handleAddCustomerConfirm = this.handleAddCustomerConfirm.bind(this);
    this.updateDataSource = this.updateDataSource.bind(this);
    this.getDataSource = this.getDataSource.bind(this);
    this.getDataSourceBySearch = this.getDataSourceBySearch.bind(this);
    this.getCustomerDataSource = this.getCustomerDataSource.bind(this);
  }

  componentDidMount() {
    const current = this.state.current,
          pageSize = this.state.pageSize;

    this.getDataSource(current, pageSize);
    this.getCustomerDataSource();
  }

  handleSave(field) {
    updateCompanyInfo('PUT', {
      id: field.id,
      update_info: [{ key: field.fieldProp, value: field.fieldValue }]
    }, json => {
      if (json.code === 200) {
        message.success(language.SAVE_SUCCESS_MSG);
        this.updateDataSource();
      } else {
        message.error(language.SAVE_FAIL_MSG);
      }
    });
  }

  handleRemove(id, key, value, date) {
    updateCompanyInfo('DELETE', {
      id: id,
      key: key,
      value: value,
      date: date
    }, json => {
      if (json.code === 200) {
        message.success(language.DELETE_SUCCESS_MSG);
        this.updateDataSource();
      } else {
        message.error(language.DELETE_FAIL_MSG);
      }
    });
  }

  handleSeachClick(value) {
    const pageSize = this.state.pageSize,
          current = 1;

    this.setState({
      searchWord: value,
      loading: true,
      current: current,
      pageSize: pageSize
    });

    if (value) {
      this.getDataSourceBySearch(value, current, pageSize);
    } else {
      this.getDataSource(current, pageSize);
    }
  }

  handleShowSizeChange(current, pageSize) {
    const searchWord = this.state.searchWord.trim();

    this.setState({
      current: current,
      pageSize: pageSize
    });

    if (searchWord === '') {
      this.getDataSource(current, pageSize);
    } else {
      this.getDataSourceBySearch(searchWord, current, pageSize);
    }
  }

  handlePaginationChange(current) {
    const pageSize = this.state.pageSize,
          searchWord = this.state.searchWord.trim();

    this.setState({
      current: current
    });

    if (searchWord === '') {
      this.getDataSource(current, pageSize);
    } else {
      this.getDataSourceBySearch(searchWord, current, pageSize);
    }
  }

  handleCreateCompanySubmit(fieldValues) {
    const { current, pageSize } = this.state;
          
    this.setState({
      createCompanyConfirmLoading: true
    });

    createCompany(fieldValues, (json) => {
      if (json.code === 200) {
        message.success(language.ADD_SUCCESS_MSG);
        this.getDataSource(current, pageSize);
      } else {
        message.error(language.ADD_FAIL_MSG);
      }
      this.setState({
        createCompanyConfirmLoading: false
      });
    });
  }

  handleUploadBtnClick() {
    this.setState({
      visible: true
    });
  }

  handleUploadModalCancel() {
    this.setState({
      visible: false
    });
  }

  handleAddCustomerConfirm(id) {
    let idList = this.state.customerIDList;

    updateCustomer('POST', {
      id: id
    }, (json) => {
      if (json.code === 200) {
        message.success(language.ADD_SUCCESS_MSG);
        idList.push(id);
        this.setState({
          customerIDList: idList
        });
      } else {
        message.error(language.ADD_FAIL_MSG);
      }
    });
  }

  updateDataSource() {
    const searchWord = this.state.searchWord.trim(),
          current = this.state.current,
          pageSize = this.state.pageSize;
    
    if (searchWord === '') {
      this.getDataSource(current, pageSize);
    } else {
      this.getDataSourceBySearch(searchWord, current, pageSize);
    }
  }

  getDataSource(current, pageSize) {
    this.setState({
      loading: true
    });

    getAllCompany({
      current_page: current,
      page_size: pageSize
    }, (json) => {
      if (json.code === 200) {
        this.setState({
          dataSource: json.data,
          total: json.total,
          loading: false
        });
      }
    });
  }

  getDataSourceBySearch(searchWord, current, pageSize) {
    this.setState({
      loading: true
    });

    getAllCompanyBySearch({
      current_page: current,
      page_size: pageSize,
      search_text: searchWord
    }, json => {
      if (json.code === 200) {
        this.setState({
          dataSource: json.data,
          total: json.total,
          loading: false
        });
      }
    });
  }

  getCustomerDataSource() {
    getCustomerList(json => {
      if (json.code === 200) {
        let idList = json.data.map(v => v.id);
        this.setState({
          customerIDList: idList
        });
      }
    });
  }

  render() {
    const { current, total, visible } = this.state;

    // 主体表格分页
    const pagination = {
      current: current,
      total: total,
      showSizeChanger: true,
      showQuickJumper: true,
      defaultPageSize: 40,
      showTotal: total => `共 ${total} 条`,
      onShowSizeChange: this.handleShowSizeChange,
      onChange: this.handlePaginationChange
    };

    return (
      <div className="cs-card-inner">
        <div className="cs-card-inner-top">
          <div className="cs-card-inner-top-col-2">
            <EnhancedInput 
              type="search"
              onClick={this.handleSeachClick}
            />
          </div>
          <div className="cs-card-inner-top-col">
            <CreateNewCompany onSubmit={this.handleCreateCompanySubmit} />
          </div>
          <div className="cs-card-inner-top-col">
            <ButtonWithModal
              buttonText={language.UPLOAD}
              modalTitle={language.UPLOAD}
              visible={visible}
              onButtonClick={this.handleUploadBtnClick}
              onModalCancel={this.handleUploadModalCancel}
            >
              <Upload {...this.props.uploadProps}>
                <Button type="ghost">
                  <Icon type="upload" /> 点击上传
                </Button>
              </Upload>
            </ButtonWithModal>
          </div>
        </div>
        <div className="cs-card-inner-pagination">
          <Pagination {...pagination} />
        </div>
        <Spin
          size="large"
          spinning={this.state.loading}
        >
          {this.state.dataSource.map((item, index) => {
            return (
              <CompanyInfo
                key={index}
                dataSource={item}
                isCustomer={this.state.customerIDList.indexOf(item.id) > -1}
                onSave={this.handleSave}
                onRemove={this.handleRemove}
                onAddCustomerConfirm={this.handleAddCustomerConfirm}
              />
            );
          })}
        </Spin>
        <div className="cs-card-inner-pagination">
          <Pagination {...pagination} />
        </div>
      </div>
    );
  }
}

CompanyList.defaultProps = {
  uploadProps: {}
};

CompanyList.propTypes = {
  uploadProps: PropTypes.object
};

export default CompanyList;
