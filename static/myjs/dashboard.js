$(function(){

        $(".edit_emp").on('click', function(){
            id = $(this).attr('value')
            var data = {"emp_id":id}
            $.ajax({
                type:'POST',
                url:'/getEmp',
                contentType:'application/json',
                cache:false,
                processData:false,
                data:JSON.stringify(data),
                dataType:'json',
                success: function(data){
                    $("#emp_id").val(data['emp_id'])
                    $("#emp_name").val(data['emp_name'])
                    $("#emp_email").val(data['emp_email'])
                    $("#emp_mobile").val(data['emp_mobile'])
                    $("#modal-edit").modal('show')
                }
            });
        });


    $(".del_btn").on('click', function(){
            d_id = $(this).attr('value')
            file_name = $(this).attr('file_name')
            var data = {"id": d_id,"filename": file_name}
            $.ajax({
                type:'POST',
                url:'/deleteCSV',
                contentType:'application/json',
                cache:false,
                processData:false,
                data:JSON.stringify(data),
                dataType:'json',
                success: function(data){
                    alert(data['result'])
                    window.location.reload()
                }
            });
        });

        // demo
        $(".download_file").on('click', function(){
            d_id = $(this).attr('value')
            var data = {"id": d_id}
            $.ajax({
                type:'POST',
                url:'/download',
                contentType:'application/json',
                cache:false,
                processData:false,
                data:JSON.stringify(data),
                dataType:'json',
                success: function(data){
//                    alert(data)data
                }
            });
        })
})