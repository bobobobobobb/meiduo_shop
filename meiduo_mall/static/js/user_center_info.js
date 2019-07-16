var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host: host,
        username: username,
        mobile: mobile,
        email: email,
        //email_active: email_active,
        set_email: true,
        error_email: false,
        error_email_message: '',
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        histories: [],
        save1:'保存',
        sending_email_flag: false,
        send_email_message:'请点击按钮,激活邮箱',
        set_email_flag: false,
    },
    // ES6语法
    mounted() {
        // 额外处理用户数据
        this.email_active = (this.email_active=='True') ? true : false;
        this.set_email = (this.email=='') ? true : false;
        this.check_email_content();
        this.see_state();
        //this.set_email = true
        // 请求浏览历史记录
        //this.browse_histories();
    },
    methods: {
        //查看验证状态
        see_state(){
            if(this.email == ''){
                return
            }
            var url = '/see_state/';
            axios.get(url).then(response =>{
                if(response.data.code == 0){
                    this.set_email = false;
                    this.set_email_flag = true;
                }else {
                 if(response.data.code == 1) {
                    this.set_email = false;
                    this.set_email_flag = false;}
                }
            }).catch(error => {
              alert('error')
            })
        },
        //send_active_email 发送激活邮件
        send_active_email(){
            if (this.email != ''){
            if(this.send_email_btn_disabled = true){
                this.sending_email_flag = false;
                this.send_email_message = '请点击按钮,激活邮箱';
                this.save1_email();
                var url = '/save_email/';
                axios.put(url, {
                    email:this.email,
                },{
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                }).then(response => {
                    if(response.data.code == 0){
                        //激活成功
                        this.sending_email_flag = true;
                        this.send_email_message ='邮件发送成功,请去邮箱进行点击激活'
                        //alert('发送短信成功')

                        //this.set_email = false
                    }
                }).catch(error => {
                    alert('发送激活链接失败')
                    this.sending_email_flag = false
                })

            }else {
                this.sending_email_flag = true;
            }}else {
                alert('请输入邮箱')
            }
        },
        //判断email是否有值
        check_email_content(){
          if(this.email != ''){
              this.save1 = '已保存';
              this.send_email_btn_disabled = true;
              this.set_email = false;
          }else {
              this.save1 = '保存';
              this.send_email_btn_disabled = false;
              this.set_email = true
          }
        },
        //cancel1_email
        cancel1_email(){
            var url = '/save_email/?email='+ this.email;
            axios.get(url).then(response => {
                if(response.data.code == 0){
                    //取消保存成功
                    this.email = '';
                    this.check_email_content();
                    this.sending_email_flag = false;
                    this.send_email_message = '请点击按钮,激活邮箱';
                    this.set_email = true

                }
            }).catch(error => {
                alert('取消失败')
            })
        },
        //保存邮箱到数据库  向后端发起请求
        save1_email(){
            this.check_email();
            var url = '/save_email/'
            axios.post(url, {
                email:this.email
            },{
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json'
            }).then(response => {
                if(response.data.code == '0'){
                    //保存邮箱成功
                    this.send_email_btn_disabled = true;
                    this.save1 = '已保存';
                    this.set_email = true
                }else {
                    if(response.data.code == '5001'){
                        alert('邮箱格式错误');
                        this.email = ''
                    }
                }
            }).catch(error => {
                alert('保存邮箱失败')
            })
        },
        // 检查email格式
        check_email(){
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.set_email = true
            } else {
                // this.error_email_message = '邮箱格式错误';
                // this.error_email = true;
                //return;
                alert('请你输入正确的邮箱')
            }
        },
        // 取消保存
        cancel_email(){
            this.email = '';
            this.error_email = false;
        },
        // 保存email
        // save_email(){
        //     // 检查email格式
        //     this.check_email();
        //
        //     if (this.error_email == false) {
        //         var url = this.host + '/emails/';
        //         axios.put(url, {
        //                 email: this.email
        //             }, {
        //                 headers: {
        //                     'X-CSRFToken':getCookie('csrftoken')
        //                 },
        //                 responseType: 'json'
        //             })
        //             .then(response => {
        //                 if (response.data.code == '0') {
        //                     this.set_email = false;
        //                     this.send_email_btn_disabled = true;
        //                     this.send_email_tip = '已发送验证邮件';
        //                 } else if (response.data.code == '4101') {
        //                     location.href = '/login/?next=/info/';
        //                 } else { // 5000 5001
        //                     this.error_email_message = response.data.errmsg;
        //                     this.error_email = true;
        //                 }
        //             })
        //             .catch(error => {
        //                 console.log(error.response);
        //             });
        //     }
        // },
        // 请求浏览历史记录
        browse_histories(){
            var url = this.host + '/browse_histories/';
            axios.get(url, {
                    responseType: 'json'
                })
                .then(response => {
                    this.histories = response.data.skus;
                    for(var i=0; i<this.histories.length; i++){
                        this.histories[i].url = '/goods/' + this.histories[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        }
    }
});
