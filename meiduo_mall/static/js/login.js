var vm = new Vue({
    el: '#app',
	// 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        error_username: false,
        error_password: false,
		error_username_message: '请输入5-20个字符的用户名',
		error_password_message: '请输入8-12位的密码',
        username: '',
        password: '',
        remembered: true,
        qq_url:'',
    },
    methods: {
        // 检查账号
        check_username: function(){
        	var re = /^[a-zA-Z0-9_-]{5,20}/;
			if (re.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_username = true;
            }
        },
		// 检查密码
        check_pwd: function(){
        	var re = /^[0-9A-Za-z]{8,20}$/;
			if (re.test(this.password)) {
                this.error_pwd = false;
            } else {
                this.error_pwd = true;
            }
        },
        // 表单提交
        on_submit: function(){
            this.check_username();
            this.check_pwd();

            if (this.error_username == true || this.error_pwd == true) {
                // 不满足登录条件：禁用表单
				window.event.returnValue = false;
                alert('你输入的信息不全')
            }
        },
        // qq登录
        // qq_login: function(){
        //     var next = get_query_string('next') || '/';
        //     var url = this.host + '/qq/login/?next=' + next;
        //     axios.get(url, {
        //             responseType: 'json'
        //         })
        //         .then(response => {
        //             location.href = response.data.login_url;
        //         })
        //         .catch(error => {
        //             console.log(error.response);
        //         })
        // }


        //实现qq登陆
        qq_login:function () {
            //https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&state=test&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8000%2Foauth_callback&client_id=101518219
            //https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&state=test&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8000%2Foauth_callback&client_id=101518219
            //'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test'
            //show?which=Login&display=pc&state=test&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8000%2Foauth_callback
            //authorize?redirect_uri=http://www.meiduo.site:8000/oauth_callback&state=test'
            //var next = get_query_string('next') || '/';
            //var url = this.host + '/qq_login/?next=' + next;
            var url = this.host + '/qq_login/';
            axios.get(url,{
                responseType: 'json'
            }).then(response => {
                location.href = response.data.url
                alert(this.qq_url)
            }).catch(error => {
                    console.log(error.response);
                })
        }
    }
});
