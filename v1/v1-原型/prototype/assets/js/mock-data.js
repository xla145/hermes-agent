/**
 * 智能物流管理系统 - Mock 数据
 */

// 模拟用户数据
const mockUser = {
    id: 1,
    username: 'admin',
    name: '管理员',
    role: 'admin',
    roleName: '系统管理员',
    department: '总部'
};

// 模拟订单数据
const mockOrders = [
    {
        id: 'ORD20240525005',
        orderNo: 'ORD20240525005',
        customerName: '深圳科技有限公司',
        customerId: 'C001',
        goodsInfo: '电子产品 20箱',
        goodsName: '电子产品',
        goodsQuantity: 20,
        goodsWeight: 200,
        fromCity: '深圳',
        fromAddress: '南山区科技园A座',
        fromContact: '张三',
        fromPhone: '13800138001',
        toCity: '上海',
        toAddress: '浦东新区张江高科',
        toContact: '李四',
        toPhone: '13800138002',
        status: 'in_transit',
        statusText: '运输中',
        createTime: '2024-05-25 10:30',
        createTimeRaw: new Date('2024-05-25T10:30:00'),
        vehicleNo: '粤B12345',
        driverName: '王师傅',
        driverPhone: '13900139001'
    },
    {
        id: 'ORD20240525004',
        orderNo: 'ORD20240525004',
        customerName: '广州贸易公司',
        customerId: 'C002',
        goodsInfo: '服装 50箱',
        goodsName: '服装',
        goodsQuantity: 50,
        goodsWeight: 500,
        fromCity: '广州',
        fromAddress: '天河区珠江新城',
        fromContact: '王五',
        fromPhone: '13800138003',
        toCity: '北京',
        toAddress: '朝阳区CBD',
        toContact: '赵六',
        toPhone: '13800138004',
        status: 'dispatched',
        statusText: '已派单',
        createTime: '2024-05-25 09:15',
        createTimeRaw: new Date('2024-05-25T09:15:00')
    },
    {
        id: 'ORD20240525003',
        orderNo: 'ORD20240525003',
        customerName: '东莞电子厂',
        customerId: 'C003',
        goodsInfo: '原材料 30吨',
        goodsName: '原材料',
        goodsQuantity: 30,
        goodsWeight: 30000,
        fromCity: '东莞',
        fromAddress: '松山湖工业区',
        fromContact: '陈七',
        fromPhone: '13800138005',
        toCity: '杭州',
        toAddress: '滨江区高新园区',
        toContact: '周八',
        toPhone: '13800138006',
        status: 'pending',
        statusText: '待派单',
        createTime: '2024-05-25 08:45',
        createTimeRaw: new Date('2024-05-25T08:45:00')
    },
    {
        id: 'ORD20240525002',
        orderNo: 'ORD20240525002',
        customerName: '佛山制造公司',
        customerId: 'C004',
        goodsInfo: '机械设备 2台',
        goodsName: '机械设备',
        goodsQuantity: 2,
        goodsWeight: 5000,
        fromCity: '佛山',
        fromAddress: '顺德区工业园',
        fromContact: '吴九',
        fromPhone: '13800138007',
        toCity: '南京',
        toAddress: '江宁区开发区',
        toContact: '郑十',
        toPhone: '13800138008',
        status: 'completed',
        statusText: '已完成',
        createTime: '2024-05-24 16:20',
        createTimeRaw: new Date('2024-05-24T16:20:00'),
        completeTime: '2024-05-25 14:30'
    },
    {
        id: 'ORD20240525001',
        orderNo: 'ORD20240525001',
        customerName: '珠海进出口公司',
        customerId: 'C005',
        goodsInfo: '办公用品 100箱',
        goodsName: '办公用品',
        goodsQuantity: 100,
        goodsWeight: 800,
        fromCity: '珠海',
        fromAddress: '香洲区商业中心',
        fromContact: '孙一',
        fromPhone: '13800138009',
        toCity: '武汉',
        toAddress: '光谷科技园区',
        toContact: '孙二',
        fromPhone: '13800138010',
        status: 'pending',
        statusText: '待派单',
        createTime: '2024-05-24 14:00',
        createTimeRaw: new Date('2024-05-24T14:00:00')
    },
    {
        id: 'ORD20240524008',
        orderNo: 'ORD20240524008',
        customerName: '中山电器公司',
        customerId: 'C006',
        goodsInfo: '电器元件 500件',
        goodsName: '电器元件',
        goodsQuantity: 500,
        goodsWeight: 300,
        fromCity: '中山',
        fromAddress: '火炬开发区',
        fromContact: '周强',
        fromPhone: '13800138011',
        toCity: '成都',
        toAddress: '高新区天府软件园',
        toContact: '刘洋',
        toPhone: '13800138012',
        status: 'in_transit',
        statusText: '运输中',
        createTime: '2024-05-24 10:00',
        createTimeRaw: new Date('2024-05-24T10:00:00'),
        vehicleNo: '粤T67890',
        driverName: '张师傅',
        driverPhone: '13900139002'
    },
    {
        id: 'ORD20240524007',
        orderNo: 'ORD20240524007',
        customerName: '惠州化工厂',
        customerId: 'C007',
        goodsInfo: '化工原料 20吨',
        goodsName: '化工原料',
        goodsQuantity: 20,
        goodsWeight: 20000,
        fromCity: '惠州',
        fromAddress: '大亚湾工业区',
        fromContact: '林总',
        fromPhone: '13800138013',
        toCity: '重庆',
        toAddress: '两江新区工业园',
        toContact: '黄总',
        toPhone: '13800138014',
        status: 'cancelled',
        statusText: '已取消',
        createTime: '2024-05-24 09:00',
        createTimeRaw: new Date('2024-05-24T09:00:00'),
        cancelReason: '客户取消订单'
    },
    {
        id: 'ORD20240524006',
        orderNo: 'ORD20240524006',
        customerName: '江门食品公司',
        customerId: 'C008',
        goodsInfo: '食品 80箱',
        goodsName: '食品',
        goodsQuantity: 80,
        goodsWeight: 600,
        fromCity: '江门',
        fromAddress: '蓬江区',
        fromContact: '李总',
        fromPhone: '13800138015',
        toCity: '西安',
        toAddress: '经开区',
        toContact: '王总',
        toPhone: '13800138016',
        status: 'waiting_sign',
        statusText: '待签收',
        createTime: '2024-05-23 16:00',
        createTimeRaw: new Date('2024-05-23T16:00:00'),
        vehicleNo: '粤J11111',
        driverName: '赵师傅',
        driverPhone: '13900139003'
    }
];

// 模拟车辆数据
const mockVehicles = [
    {
        id: 'V001',
        vehicleNo: '粤B12345',
        vehicleType: '厢式货车',
        loadCapacity: 5000,
        volume: 20,
        gpsDevice: 'GPS-001',
        status: 'in_transit',
        statusText: '运输中',
        driver: '王师傅',
        driverPhone: '13900139001',
        currentLocation: '湖南省长沙市'
    },
    {
        id: 'V002',
        vehicleNo: '粤B67890',
        vehicleType: '平板车',
        loadCapacity: 10000,
        volume: 30,
        gpsDevice: 'GPS-002',
        status: 'idle',
        statusText: '空闲',
        driver: null,
        driverPhone: null,
        currentLocation: '深圳市宝安区'
    },
    {
        id: 'V003',
        vehicleNo: '粤T67890',
        vehicleType: '冷藏车',
        loadCapacity: 3000,
        volume: 15,
        gpsDevice: 'GPS-003',
        status: 'in_transit',
        statusText: '运输中',
        driver: '张师傅',
        driverPhone: '13900139002',
        currentLocation: '湖北省武汉市'
    },
    {
        id: 'V004',
        vehicleNo: '粤J11111',
        vehicleType: '厢式货车',
        loadCapacity: 5000,
        volume: 20,
        gpsDevice: 'GPS-004',
        status: 'in_transit',
        statusText: '运输中',
        driver: '赵师傅',
        driverPhone: '13900139003',
        currentLocation: '陕西省西安市'
    },
    {
        id: 'V005',
        vehicleNo: '粤S22222',
        vehicleType: '平板车',
        loadCapacity: 8000,
        volume: 25,
        gpsDevice: 'GPS-005',
        status: 'maintenance',
        statusText: '维修中',
        driver: null,
        driverPhone: null,
        currentLocation: '广州市天河区'
    },
    {
        id: 'V006',
        vehicleNo: '粤A33333',
        vehicleType: '厢式货车',
        loadCapacity: 5000,
        volume: 20,
        gpsDevice: 'GPS-006',
        status: 'idle',
        statusText: '空闲',
        driver: '钱师傅',
        driverPhone: '13900139004',
        currentLocation: '广州市白云区'
    },
    {
        id: 'V007',
        vehicleNo: '粤B44444',
        vehicleType: '冷藏车',
        loadCapacity: 3000,
        volume: 15,
        gpsDevice: 'GPS-007',
        status: 'offline',
        statusText: '离线',
        driver: '孙师傅',
        driverPhone: '13900139005',
        currentLocation: '未知'
    },
    {
        id: 'V008',
        vehicleNo: '粤C55555',
        vehicleType: '平板车',
        loadCapacity: 12000,
        volume: 35,
        gpsDevice: 'GPS-008',
        status: 'idle',
        statusText: '空闲',
        driver: '周师傅',
        driverPhone: '13900139006',
        currentLocation: '佛山市禅城区'
    }
];

// 模拟司机数据
const mockDrivers = [
    {
        id: 'D001',
        name: '王师傅',
        phone: '13900139001',
        idCard: '44010***********1234',
        driverLicense: 'A2',
        qualificationCert: '货运从业资格证',
        status: 'on_duty',
        statusText: '在岗',
        vehicleNo: '粤B12345',
        totalOrders: 156,
        onTimeRate: '96%'
    },
    {
        id: 'D002',
        name: '张师傅',
        phone: '13900139002',
        idCard: '44010***********5678',
        driverLicense: 'A2',
        qualificationCert: '货运从业资格证',
        status: 'on_duty',
        statusText: '在岗',
        vehicleNo: '粤T67890',
        totalOrders: 203,
        onTimeRate: '94%'
    },
    {
        id: 'D003',
        name: '赵师傅',
        phone: '13900139003',
        idCard: '44010***********9012',
        driverLicense: 'B2',
        qualificationCert: '货运从业资格证',
        status: 'on_duty',
        statusText: '在岗',
        vehicleNo: '粤J11111',
        totalOrders: 178,
        onTimeRate: '95%'
    },
    {
        id: 'D004',
        name: '钱师傅',
        phone: '13900139004',
        idCard: '44010***********3456',
        driverLicense: 'A2',
        qualificationCert: '货运从业资格证',
        status: 'on_duty',
        statusText: '在岗',
        vehicleNo: '粤A33333',
        totalOrders: 89,
        onTimeRate: '92%'
    },
    {
        id: 'D005',
        name: '孙师傅',
        phone: '13900139005',
        idCard: '44010***********7890',
        driverLicense: 'B2',
        qualificationCert: '货运从业资格证',
        status: 'rest',
        statusText: '休息',
        vehicleNo: null,
        totalOrders: 234,
        onTimeRate: '97%'
    },
    {
        id: 'D006',
        name: '周师傅',
        phone: '13900139006',
        idCard: '44010***********1235',
        driverLicense: 'A1',
        qualificationCert: '货运从业资格证',
        status: 'on_duty',
        statusText: '在岗',
        vehicleNo: '粤C55555',
        totalOrders: 167,
        onTimeRate: '93%'
    },
    {
        id: 'D007',
        name: '吴师傅',
        phone: '13900139007',
        idCard: '44010***********1236',
        driverLicense: 'A2',
        qualificationCert: '货运从业资格证',
        status: 'rest',
        statusText: '休息',
        vehicleNo: null,
        totalOrders: 145,
        onTimeRate: '91%'
    },
    {
        id: 'D008',
        name: '郑师傅',
        phone: '13900139008',
        idCard: '44010***********1237',
        driverLicense: 'B2',
        qualificationCert: '货运从业资格证',
        status: 'on_duty',
        statusText: '在岗',
        vehicleNo: null,
        totalOrders: 98,
        onTimeRate: '90%'
    }
];

// 模拟异常数据
const mockExceptions = [
    {
        id: 'EXC001',
        exceptionNo: 'EXC20240525001',
        orderNo: 'ORD20240524008',
        type: 'delay',
        typeText: '运输延迟',
        description: '因天气原因，高速公路封闭，预计延迟2小时到达',
        status: 'pending',
        statusText: '待处理',
        createTime: '2024-05-25 14:30',
        reporter: '张师傅',
        order: mockOrders[5]
    },
    {
        id: 'EXC002',
        exceptionNo: 'EXC20240524002',
        orderNo: 'ORD20240524003',
        type: 'route_deviation',
        typeText: '路线偏离',
        description: '车辆偏离预定路线超过5公里',
        status: 'processing',
        statusText: '处理中',
        createTime: '2024-05-24 18:00',
        reporter: '系统自动',
        handleTime: '2024-05-24 18:30',
        handler: '调度员小李',
        solution: '已联系司机重新规划路线',
        order: null
    },
    {
        id: 'EXC003',
        exceptionNo: 'EXC20240523003',
        orderNo: 'ORD20240523005',
        type: 'goods_damage',
        typeText: '货物异常',
        description: '货物包装破损，需要重新包装',
        status: 'handled',
        statusText: '已处理',
        createTime: '2024-05-23 10:00',
        reporter: '王师傅',
        handleTime: '2024-05-23 12:00',
        handler: '调度员小王',
        solution: '已重新包装货物，客户确认无异议',
        order: null
    }
];

// 模拟回单数据
const mockReceipts = [
    {
        id: 'RCP001',
        orderNo: 'ORD20240524006',
        customerName: '江门食品公司',
        uploadTime: '2024-05-25 16:00',
        imageUrl: '/assets/images/receipt-placeholder.jpg',
        status: 'pending',
        statusText: '待确认',
        signer: '王总',
        signTime: '2024-05-25 15:30'
    },
    {
        id: 'RCP002',
        orderNo: 'ORD20240523008',
        customerName: '长沙贸易公司',
        uploadTime: '2024-05-24 10:00',
        imageUrl: '/assets/images/receipt-placeholder.jpg',
        status: 'confirmed',
        statusText: '已确认',
        signer: '李总',
        signTime: '2024-05-24 09:45',
        confirmTime: '2024-05-24 10:30',
        confirmUser: '仓库管理员小张'
    }
];

// 订单状态枚举
const orderStatus = [
    { value: 'pending', label: '待派单' },
    { value: 'dispatched', label: '已派单' },
    { value: 'in_transit', label: '运输中' },
    { value: 'arrived', label: '已到达' },
    { value: 'waiting_sign', label: '待签收' },
    { value: 'completed', label: '已完成' },
    { value: 'cancelled', label: '已取消' }
];

// 车辆状态枚举
const vehicleStatus = [
    { value: 'idle', label: '空闲' },
    { value: 'in_transit', label: '运输中' },
    { value: 'maintenance', label: '维修中' },
    { value: 'offline', label: '离线' }
];

// 司机状态枚举
const driverStatus = [
    { value: 'on_duty', label: '在岗' },
    { value: 'rest', label: '休息' },
    { value: 'off_duty', label: '离职' }
];

// 异常类型枚举
const exceptionType = [
    { value: 'delay', label: '运输延迟' },
    { value: 'route_deviation', label: '路线偏离' },
    { value: 'goods_damage', label: '货物异常' },
    { value: 'vehicle_breakdown', label: '车辆故障' },
    { value: 'other', label: '其他' }
];

// 运输里程碑
const mockMilestones = [
    { status: 'created', title: '订单创建', time: '2024-05-25 10:30', completed: true },
    { status: 'dispatched', title: '已派单', time: '2024-05-25 11:00', completed: true },
    { status: 'loaded', title: '已装车', time: '2024-05-25 14:00', completed: true },
    { status: 'in_transit', title: '运输中', time: '2024-05-25 14:30', completed: true, current: true },
    { status: 'arrived', title: '已到达', time: null, completed: false },
    { status: 'signed', title: '签收完成', time: null, completed: false }
];

// 导出数据
window.mockData = {
    user: mockUser,
    orders: mockOrders,
    vehicles: mockVehicles,
    drivers: mockDrivers,
    exceptions: mockExceptions,
    receipts: mockReceipts,
    status: {
        order: orderStatus,
        vehicle: vehicleStatus,
        driver: driverStatus,
        exception: exceptionType
    },
    milestones: mockMilestones
};