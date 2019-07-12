var app = new Vue({
        el:'#app',
        delimiters:['[[',']]'],
        data:{
            // host: host,
            error_name: false,
            error_password: false,
            error_password2: false,
            error_check_password: false,
            error_mobile: false,
            error_code:false,
            // error_image_code: false,
            // error_sms_code: false,
            // error_allow: false,
            error_name_message: '请输入5-20个字符的用户',
            error_password_message: '请输入8-20位的密码',
            error_password2_message: '两次输入的密码不一致',
            error_mobile_message: '请输入正确的手机号码',
            error_code_message:'请填写图形验证码',
            // error_image_code_message: '请填写图形验证码',
            // error_sms_code_message: '请填写短信验证码',
            // error_allow_message: '请勾选用户协议',
            image_code_id: '',
            image_code_url: '',
            // sms_code_tip: '获取短信验证码',
            // sending_flag: false,
            username: '',
            password: '',
            password2: '',
            mobile: '',
            pic_code:'',
            send_sms:'获取短信验证码',

            // image_code: '',
            // sms_code: '',
            // allow: true


        },
        mounted: function () {
        // 向服务器获取图片验证码
        this.generate_image_code();
    },
        methods:{
            // 生成uuid
            generateUUID: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
            //生成图形验证码
            generate_image_code:function () {
                this.image_code_id = this.generateUUID()
                this.image_code_url = '/vertify/'+ this.image_code_id + '/';
                console.log(this.image_code_url)


            },
            //获取短信验证码
            get_sms_code:function () {
                this.check_mobile();
                this.code_check();
                if(this.error_mobile == true || this.error_code == true){
                    alert('你输入的信息不全');
                    return
                }
                //向后端发起post请求 参数有手机号 图片验证码 uuid 返回数据类型为json,当收到响应时,设置定时器
                //拼接url
                var url = '/get_sms_code/';
                axios.post(url, {
                    mobile:this.mobile,
                    uuid:this.image_code_id,
                    pic_code:this.pic_code
                },{
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                }).then(response => {
                    // alert(response.data.code);
                    if(response.data.code == 1){
                        var num = 60;
                        var t = setInterval(()=>{
                            if(num==0){
                                clearInterval(t)
                                // this.seng_flag = false
                                this.send_sms = '获取验证码'

                            }else {
                                num -= 1;
                                this.send_sms = num + '秒'
                            }
                        }, 1000,60)
                    }else {
                        if(response.data.code == 4001){
                            this.generate_image_code();
                            alert('输入验证码错误')
                        }else {
                            if(response.data.code == 4002){
                                this.generate_image_code();
                                alert('短信发送频繁')
                            }
                        }


                    }
                }).catch(error => {
                    alert('发送post请求失败')
                })
            },
            // 检查用户名
            check_username: function () {
                var re = /^[a-zA-Z0-9_-]{5,20}$/;
                if (re.test(this.username)) {
                    this.error_name = false;
                    // GET  /register/username/count/
                    var url = '/register/'+ this.username +'/count/';
                    axios.get(url).then(response => {
                    if(response.data.count==1){
                        this.username='';
                        this.error_name = true;
                        this.error_name_message = '用户名重复了';
                    }else{
                        this.error_name = false;
                    }
                }).catch(error => {
                    alert('error');
                })
                } else {
                    this.error_name = true;
                    //this.error_name_message = '请输入5-20个字符的用户名';
                    this.username = '';

                }

                },
            // 检查密码
            check_password:function () {
                var re = /^[a-zA-Z0-9-_]{8,20}$/;
                if(re.test(this.password)) {
                    this.error_password = false;

                } else {
                    this.error_password = true;
                    this.password = '';

                };
            },
            //校验密码是否一致
            check_password2:function () {
                if (this.password2 != this.password){
                    this.error_password2=true;
                    this.password2 = '';

                }else {
                    this.error_password2=false;
                }
            },
            // 校验手机号
            check_mobile:function () {
                var re = /^1[3|4|5]\d{9}$/;
                if(re.test(this.mobile)){
                    this.error_mobile=false;
                    //输入不为空时  可以判断手机号是否重复   通过post请求进行判断
                    var url = '/check_mobile/';
                    axios.post(url, {
                        // 携带的参数
                        mobile:this.mobile,
                    },{
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                }).then(response => {
                    if(response.data.code == '1'){
                        //当返回值为1时,手机号重复
                        this.error_mobile = true
                        this.error_mobile_message = '该手机号已经被注册'
                        this.mobile = ''
                    }else {
                        //当返回值为0, 手机号不重复
                        this.error_mobile = false

                    }
                    }).catch(error => {
                        alert('网络故障,请重新输入手机号')
                        this.mobile = ''

                    })

                }else {
                    this.error_mobile=true;
                    this.mobile = '';
                    this.error_mobile_message = '请您输入手机号';
                }
            },
            //校验手机号是否重复

            // 校验图形验证码
            code_check:function () {
                if(this.pic_code==''){
                    this.error_code=true;


                }else {
                    this.error_code=false;

                    // axios.get(this.image_code_url).then(response =>{
                    //     response.data.
                    // }).catch(error =>{
                    //
                    // })
                }
            }


        }
    })